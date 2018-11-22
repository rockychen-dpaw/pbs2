from dateutil import tz
import unicodecsv

from django import http

from dpaw_utils.views import (CreateView,ListView,UpdateView,ReadonlyView)

from pbs.report.models import Evaluation
from pbs.views import (ListActionMixin,FormActionMixin)
from ..models import (Prescription,)
from ..forms import (PrescriptionCreateForm,PrescriptionFilterForm,PrescriptionListForm,PrescriptionViewForm)
from ..filters import (PrescriptionFilter,)

class PrescriptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionCreateForm
    template_name_suffix = "_create"

class PrescriptionHomeView(ReadonlyView):
    urlname = "{}_home"
    model = Prescription
    form_class = PrescriptionViewForm
    template_name_suffix = "_home"
    title = "ePFP Overview"
    context_object_name = "prescription"

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
    
