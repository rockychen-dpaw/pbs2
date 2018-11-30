function submitform(field,callback,failedCallback) {
    var formdata = $(field.form).serializeArray()
    fieldId = $(field).prop('id')
    fieldName = $(field).prop('name')
    formdata.push({"name":"submit_field","value":fieldName})
    $(field).prop('disabled',true)

    try {
        $.ajax({
          type: "POST",
          url: '',
          dataType: "json",
          data: formdata,
          error: function (xhr,status,message) {
            failedCallback(xhr.responseText || message,callback)
            $(field).prop('disabled',false)
        
          },
          success:function(data) {
              callback(data);
              $(field).prop('disabled',false)
          }
        });
    } catch(ex) {
        $(field).prop('disabled',false)
        failedCallback(ex)
    }
}


function submit_summary(field,stateSummaryObj) {
    var select = $(field)
    var fieldName = $(field).prop("name")
    var fieldValue = select.val();
    var _func = function(data) {
        console.log(data);
        if (data.errors) {
            select.parent().prev('th').children('.text-error').remove();
            var errors = [];
            for (var error in data.errors) {
              errors.push($('<p style="white-space:pre">').text(' ' + data.errors[error].join(", ")).prepend(
                $('<i>').addClass('icon-warning-sign')).addClass('text-error'));
            }
            select.parent().prev('th').append(errors);
            select.val(select.data('lastSelected'));
        } else {
            select.parent().prev('th').children('.text-error').remove();

            var selects = $('select');
            var total = selects.filter(function() {
                return $(this).val() === 'True' || $(this).val() === 'False';
              }).length;
            var complete = selects.filter(function() {
                return $(this).val() === 'True';
              }).length;
            stateSummaryObj.text(complete + '/' + total);
            selects.each(function(i, element) {
              var row = $(this).parent().parent();
              if ($(this).val() === 'True') {
                row.removeClass('error info').addClass('success');
              } else if ($(this).val() === 'False') {
                row.removeClass('success info').addClass('error');
              } else {
                row.removeClass('success error').addClass('info');
              }
            });
            select.data('lastSelected', fieldValue);
        }
    }
    submitform(field,_func,function(ex){
        errors = {}
        errors[fieldName] = [ex]
        data = {"errors":errors}
        _func(data)
    })
}

function submit_pre_state(field) {
    submit_summary(field,$('#summary-dropdown .label'))
}
function submit_day_state(field) {
    submit_summary(field,$('#implementation-dropdown .label'))
}
function submit_post_state(field) {
    submit_summary(field,$('#closure-dropdown .label'))
}
