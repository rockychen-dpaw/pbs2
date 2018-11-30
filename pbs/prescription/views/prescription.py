from dateutil import tz
import unicodecsv
import logging
import os
import subprocess

from django import http
from django.urls import path 
from django.http.response import (HttpResponse,)
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext

from dpaw_utils.views import (RequestActionMixin,CreateView,ListView,UpdateView,ReadonlyView)

from pbs.report.models import Evaluation
from pbs.views import (ListActionMixin,FormActionMixin)
from pbs import mutex, SemaphoreException
import pbs.forms

from ..models import (Prescription,)
from ..forms import (PrescriptionCreateForm,PrescriptionFilterForm,PrescriptionListForm,PrescriptionViewForm,PrescriptionUpdateForm,DraftPrescriptionUpdateForm)
from ..filters import (PrescriptionFilter,)

class PrescriptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionCreateForm
    template_name_suffix = "_create"

class PrescriptionHomeView(RequestActionMixin,ReadonlyView):
    urlname = "{}_home"
    model = Prescription
    form_class = PrescriptionViewForm
    template_name_suffix = "_home"
    title = "ePFP Overview"
    context_object_name = "prescription"

    def get_action(self,action_name):
        return pbs.forms.FORM_ACTIONS.get(action_name)

    @classmethod
    def _get_extra_urlpatterns(cls):
        return [
            path('prescription/<int:pk>/download', cls.as_view(),{'action':'download'},name='prescription_download')
        ]

    def download_get(self,request,*args,**kwargs):
        logger = logging.getLogger('pbs')
        logger.debug("_________________________ START ____________________________")
        logger.debug("Starting a PDF output: {}".format(request.get_full_path()))
        template = request.GET.get("template", "pfp")
        response = HttpResponse(content_type='application/pdf')
        texname = template + ".tex"
        filename = template + ".pdf"
        now = timezone.localtime(timezone.now())
        timestamp = now.isoformat().rsplit(
            ".")[0].replace(":", "")
        downloadname = "{0}_{1}_{2}_{3}".format(
            self.object.season.replace('/', '-'), self.object.burn_id, timestamp, filename).replace(
                ' ', '_')
        error_response = HttpResponse(content_type='text/html')
        errortxt = downloadname.replace(".pdf", ".errors.txt.html")
        error_response['Content-Disposition'] = '{0}; filename="{1}"'.format("inline", errortxt)
        try:
            with mutex('pbs'+str(self.object.id), 1, self.object.burn_id, request.user):
                subtitles = {
                    "parta": "Part A - Summary and Approval",
                    "partb": "Part B - Burn Implementation Plan",
                    "partc": "Part C - Burn Closure and Evaluation",
                    "partd": "Part D - Supporting Documents and Maps"
                }
                embed = False if request.GET.get("embed") == "false" else True
                context = {
                    'current': self.object,
                    'prescription': self.object,
                    'embed': embed,
                    'headers': request.GET.get("headers", True),
                    'title': request.GET.get("title", "Prescribed Fire Plan"),
                    'subtitle': subtitles.get(template, ""),
                    'timestamp': now,
                    'downloadname': downloadname,
                    'settings': settings,
                    'baseurl': request.build_absolute_uri("/")[:-1]
                }
                #context.update(RequestContext(request))
                if request.GET.get("download", False) is False:
                    disposition = "inline"
                else:
                    disposition = "attachment"
                response['Content-Disposition'] = (
                    '{0}; filename="{1}"'.format(
                        disposition, downloadname))

                # used by JQuery to block page until download completes
                # response.set_cookie('fileDownloadToken', '_token')

                # directory should be a property of prescription model
                # so caching machinering can put outdated flag in directory
                # to trigger a cache repop next download
                directory = os.path.join(settings.MEDIA_ROOT, 'prescriptions',
                                         str(self.object.season), self.object.burn_id + os.sep)
                if not os.path.exists(directory):
                    logger.debug("Making a new directory: {}".format(directory))
                    os.makedirs(directory)
                # os.chdir(directory)
                # logger.debug("Changing directory: {}".format(directory))

                logger.debug('Starting  render_to_string step')
                err_msg = None
                try:
                    output = render_to_string(
                        "latex/" + template + ".tex", context)
                except Exception as e:
                    import traceback
                    err_msg = u"PDF tex template render failed (might be missing attachments):"
                    logger.debug(err_msg + "\n{}".format(e))

                    error_response.write(err_msg + "\n\n{0}\n\n{1}".format(e, traceback.format_exc()))
                    return error_response

                with open(directory + texname, "wb") as f:
                    f.write(output.encode('utf-8'))
                    logger.debug("Writing to {}".format(directory + texname))

                import ipdb;ipdb.set_trace()
                logger.debug("Starting PDF rendering process ...")
                cmd = ['latexmk', '-cd', '-f', '-silent', '-pdf', directory + texname]
                logger.debug("Running: {0}".format(" ".join(cmd)))
                subprocess.call(cmd)
                # filesize
                cmd = ['ls', '-s', '--block-size=M', directory + filename]
                out = subprocess.check_output(cmd)
                filesize = int(out.split('M ')[0])
                if filesize >= 10:
                    token = '_token_10'
                else:
                    token = '_token'
                logger.info('Filesize in MB: {}'.format(filesize))

                if settings.PDF_TO_FEXSRV:
                    file_url = self.pdf_to_fexsvr(directory + filename, directory + texname, downloadname, request.user.email)
                    url = request.META.get('HTTP_REFERER')  # redirect back to the current URL
                    logger.debug("__________________________ END _____________________________")
                    resp = HttpResponseRedirect(url)
                    resp.set_cookie('fileDownloadToken', token)
                    resp.set_cookie('fileUrl', file_url)
                    return resp
                else:
                    # inline http response - pdf returned to web page
                    response.set_cookie('fileDownloadToken', token)
                    logger.debug("__________________________ END _____________________________")
                    return self.pdf_to_http(directory + filename, response, error_response)

        except SemaphoreException as e:
            error_response.write("The PDF is locked. It is probably in the process of being created by another user. <br/><br/>{}".format(e))
            return error_response

    def pdf_to_http(self, filename, response, error_response):
        # Did a PDF actually get generated?
        if not os.path.exists(filename):
            logger.debug("No PDF appeared to be rendered, returning the contents of the log instead.")
            filename = filename.replace(".pdf", ".log")
            error_response.write(open(filename).read())
            return error_response

        logger.debug("Reading PDF output from {}".format(filename))
        response.write(open(filename).read())
        logger.debug("Finally: returning PDF response.")
        return response

    def pdf_to_fexsvr(self, filename, texname, downloadname, email):
        err_msg = None
        fex_filename = downloadname
        recipient = settings.FEX_MAIL
        if os.path.exists(filename):
            logger.info("Sending file to FEX server {} ...".format(filename))

            cmd = ['fexsend', '-={}'.format(downloadname), filename, recipient]  # rename from filename to downloadname on fexsrv
            logger.info("FEX cmd: {}".format(cmd))

            p = subprocess.check_output(cmd)
            time.sleep(2)  # allow some time to upload to FEX Svr
            items = p.split('\n')
            logger.info('ITEMS: {}'.format(items))
            file_url = items[([items.index(i) for i in items if 'Location' in i]).pop()].split(': ')[1]

            logger.debug("Cleaning up ...")
            cmd = ['latexmk', '-cd', '-c', texname]
            logger.debug("Running: {0}".format(" ".join(cmd)))
            subprocess.call(cmd)

            # confirm file exists on FEX server
            cmd = ['fexsend', '-l', '|', 'grep', downloadname]
            logger.info("Checking FEX server for file: {0}".format(" ".join(cmd)))
            fex_tokens = subprocess.check_output(cmd)

            filesize = None
            expiry = None
            for token in fex_tokens.split('#'):
                if downloadname in token:
                    logger.info('FEX_TOKENS: {}'.format(token))
                    filesize = ' '.join(token.split(' [')[0].split(' ')[-2:])
                    expiry = token.split('[')[1].split(']')[0].split(' ')[0]
                    fex_filename = token.strip().split(' ')[-1].strip('\n')

            if filesize == '0 MB':
                # Needed because FEX rounds down to '0 MB'
                cmd = ['ls', '-s', '--block-size=K', filename]
                out = subprocess.check_output(cmd)
                filesize = out.split('K ')[0] + ' KB'
                logger.info('Filesize in KB: {}'.format(filesize))

            subject = 'PBS: PDF File {}'.format(fex_filename)
            email_from = recipient
            email_to = [email]

            logger.info("Sending Email notification to user (of location of FEX file) ...")
            message = 'PDF File  "{0}",  can be downloaded from:\n\n\t{1}\n\nFile will be available for {2} days.\nFilesize: {3}'.format(
                fex_filename, file_url, expiry.strip('d'), filesize)
            send_mail(subject, message, email_from, email_to)
            return file_url

        else:
            err_msg = "Error: PDF tex template render failed (might be missing attachments) {0}".format(fex_filename)
            logger.error("FAILED: Sending Email notification to user ... \n" + err_msg)
            message = 'FAILED: PDF File "{}" failed to create.\n\n{}'.format(fex_filename, err_msg + '(' + downloadname + ')')
            email_from = recipient
            email_to = [email]
            send_mail(subject, message, email_from, email_to)

        
class PrescriptionUpdateView(UpdateView):
    urlpattern = "prescription/<int:pk>/summary/pre/"
    urlname = "{}_update"
    model = Prescription
    form_class = PrescriptionUpdateForm
    template_name_suffix = "_update"
    title = "Summary & Approval"
    context_object_name = "prescription"

    def get_form_class(self):
        if self.object.planning_status == Prescription.PLANNING_DRAFT or self.user.has_perm("prescription.can_admin"):
            return DraftPrescriptionUpdateForm
        else:
            return PrescriptionUpdateForm

    def get_action(self,action_name):
        return pbs.forms.FORM_ACTIONS.get(action_name)


class PrescriptionListView(ListActionMixin,ListView):
    title = "Regional Overview"
    listform_class = PrescriptionListForm
    filterform_class = PrescriptionFilterForm
    filter_class = PrescriptionFilter
    model = Prescription
    paginate_by=8

    def burn_summary_to_csv_post(self, request,*args,**kwargs):
        queryset = self.get_queryset_4_selected(request)

        response = http.HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = "attachment; filename=burn_summary.csv"

        writer = unicodecsv.writer(response, quoting=unicodecsv.QUOTE_ALL)
        writer.writerow([
            'Burn ID', 'Name of Burn', 'Area (ha)', 'Area to be treated (%)',
            'Priority', 'If Priority 1, explanatory comment*'])

        for item in queryset.order_by('priority', 'burn_id'):
            writer.writerow([
                item.burn_id, item.name, "%0.1f" % item.area, item.treatment_percentage,
                item.get_priority_display(), item.rationale if item.priority == 1 else ""
            ])

        return response

    def export_to_csv_post(self,request,*args,**kwargs):
        queryset = self.get_queryset_4_selected(request)

        # TODO: fix up the date/time formatting to use the default template
        # filters.
        local_zone = tz.tzlocal()
        response = http.HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = "attachment; filename=export.csv"

        writer = unicodecsv.writer(response, quoting=unicodecsv.QUOTE_ALL)
        writer.writerow([
            'Region', 'District', 'Name of Burn', 'Burn ID', 'Date Updated',
            'Planning Status', 'Endorsement Status', 'Approval Status',
            'Ignition Status', 'Burn Closed', 'Burn Complexity',
            'Burn Priority', 'Burn Risk', 'Contentious',
            'Contentious Rationale', 'Location of Burn',
            'Prescribing Officer', 'Year',
            'Proposed Ignition Type', 'Actual Ignition Type',
            'Fire Weather Forecast Area/s', 'Treatment %', 'Planned Burn Area',
            'Planned Burn Perimeter', 'Total Area Where Treatment Is Complete',
            'Total Treatment Activity', 'Newest treatment date',
            'Length of Edging/Perimeter',
            'Depth of Edging', 'Shire', 'Bushfire Act Zone',
            'Prohibited Period', 'Burn Purpose/s', 'Burn Objective/s',
            'Ignition Date', 'Program Allocations', 'Fuel Types',
            'Fuel Description', 'Land Tenure', 'Year Last Burnt', 'Season Last Burnt',
            'Date(s) Escaped', 'DPaW Fire Number', 'DFES Fire Number',
            'Shortcode', 'Remote Sensing Priority', 'Aircraft Burn',
            'Success Criteria', 'Success Criteria Achieved',
            'Observations Identified', 'Proposed Action',
            'Endorsement Name/s', 'Endorsement Date',
            'Approval Name/s', 'Approval Date', 'Approved Until'])

        for item in queryset:
            if item.last_season is not None:
                last_season_burnt = item.last_season
            else:
                last_season_burnt = "Unknown"
            if item.last_year is not None:
                last_year_burnt = item.last_year
            else:
                last_year_burnt = "Unknown"

            if item.is_approved:
                approved_until = date(item.current_approval.valid_to)
            else:
                approved_until = ""

            proposed_ignitions = ('"%s"' % ", ".join(
                ",".join('{0}:{1}'.format(x.seqno, ignition_type)
                         for ignition_type
                         in (x.ignition_types.all() or ("Unset",))
                         )
                for x in item.lightingsequence_set.order_by('seqno'))
            )
            actual_ignitions = ('"%s"' % ",".join(
                ",".join('{0}:{1}'.format(x.ignition.strftime('%d/%m/%Y'),
                                          ignition_type)
                         for ignition_type
                         in (x.ignition_types.all() or ("Unset",))
                         )
                for x in item.areaachievement_set.order_by('ignition'))
            )
            forecast_areas = '"%s"' % ",".join(x.name for x
                                               in item.forecast_areas.all())
            treatment_area = item.total_treatment_area
            burnt_area_estimate = item.total_burnt_area_estimate
            burnt_area_estimate_modified = item.total_burnt_area_estimate_modified
            length_of_edging = item.total_edging_length
            depth_of_edging = item.total_edging_depth
            objectives = '"%s"' % ",".join(x.objectives for x in item.objective_set.all())
            shires = '"%s"' % ",".join(x.name for x in item.shires.all())
            purposes = '"%s"' % ",".join(x.name for x in item.purposes.all())
            fuel_types = '"%s"' % ",".join(x.name for x in item.fuel_types.all())
            fuel_descriptions = '"%s"' % ",".join(
                x.fuel_description for x in item.lightingsequence_set.all())
            tenures = '"%s"' % ",".join(x.name for x in item.tenures.all())
            escape_dates = ", ".join([
                datetime.strftime(x.date_escaped, '%d/%m/%Y')
                for x in item.areaachievement_set.filter(date_escaped__isnull=False).order_by('ignition')
            ])
            dpaw_fire_nums = '"%s"' % ",".join(
                x.dpaw_fire_no for x in item.areaachievement_set
                .exclude(dpaw_fire_no__isnull=True)
                .exclude(dpaw_fire_no__exact='')
                .order_by('ignition'))
            dfes_fire_nums = '"%s"' % ",".join(
                x.dfes_fire_no for x in item.areaachievement_set
                .exclude(dfes_fire_no__isnull=True)
                .exclude(dfes_fire_no__exact='')
                .order_by('ignition'))
            success_criterias = '"%s"' % ",".join(
                x.criteria for x in item.successcriteria_set.all().order_by('id'))
            success_criteria_outcomes = '"%s"' % ",".join(
                x.criteria.criteria + ':' + x.get_achieved_display() + ':' + x.summary
                for x in Evaluation.objects
                .filter(criteria__in=item.successcriteria_set.all().order_by('id'))
                .exclude(achieved__isnull=True)
                .exclude(summary__isnull=True))
            observations = '"%s"' % ",".join(
                (x.observations or "No observation") + ':' + (x.action or "No action")
                for x in item.proposedaction_set.all().order_by('id'))
            proposed_actions = '"%s"' % ",".join(
                (x.observations or "No observation") + ':' + (x.action or "No action")
                for x in item.proposedaction_set.all().order_by('id'))
            endorsements = '"%s"' % ",".join(
                x.role.name + ':' + x.get_endorsed_display()
                for x in item.endorsement_set.all())
            approvals = '"%s"' % ",".join(
                x.creator.get_full_name() + ':' + x.valid_to.strftime('%d/%m/%Y') + '(%s)' %
                x.extension_count for x in item.approval_set.all())

            writer.writerow([
                item.region, item.district, item.name, item.burn_id,
                item.modified.astimezone(local_zone).strftime('%d/%m/%Y %H:%M:%S'),
                item.get_planning_status_display(),
                item.get_endorsement_status_display(),
                item.get_approval_status_display(),
                item.get_ignition_status_display(),
                "Yes" if item.status == item.STATUS_CLOSED else "No",
                item.maximum_complexity,
                item.get_priority_display(), item.maximum_risk,
                "Yes" if item.contentious else "No",
                item.contentious_rationale, item.location,
                item.prescribing_officer, item.financial_year,
                proposed_ignitions, actual_ignitions, forecast_areas,
                item.treatment_percentage, item.area, item.perimeter,
                treatment_area, burnt_area_estimate, burnt_area_estimate_modified,
                length_of_edging, depth_of_edging,
                shires, item.bushfire_act_zone, item.prohibited_period,
                purposes, objectives,
                actual_ignitions,
                item.allocations,
                fuel_types, fuel_descriptions,
                tenures, last_year_burnt, last_season_burnt, escape_dates,
                dpaw_fire_nums, dfes_fire_nums, item.short_code,
                item.get_remote_sensing_priority_display(),
                "Yes" if item.aircraft_burn else "No", success_criterias,
                success_criteria_outcomes, observations, proposed_actions,
                endorsements,
                item.endorsement_status_modified.astimezone(
                    local_zone).strftime('%d/%m/%Y %H:%M:%S') if item.endorsement_status_modified else "",
                approvals,
                item.approval_status_modified.astimezone(
                    local_zone).strftime('%d/%m/%Y %H:%M:%S') if item.approval_status_modified else "",
                approved_until
            ])

        return response
    
