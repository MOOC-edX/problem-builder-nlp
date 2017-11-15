/* Javascript for QuestionGeneratorXBlock. */
function QuestionGeneratorXBlock(runtime, xblockElement) {
	"use strict";



	var student_answer_textarea_element = $(xblockElement).find('textarea[name=student_answer]');
    var teacher_answer_div_element = $(xblockElement).find('div[name=teacher_answer_div]');
    var show_answer_button = $(xblockElement).find('input[name=show_answer-button]');


	function handleSubmissionResult(results) {
		console.log('handleSubmissionResult INVOKED');
    	$(xblockElement).find('div[name=attempt-number]').text(results['attempt_number']);
    	$(xblockElement).find('div[name=problem-progress]').text(results['point_string']);
    	$(xblockElement).find('input[name=submit-button]').val("Submit")
    	if (results['submit_disabled'] == 'disabled') {
    		$(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
    	}
    	else
    	{
    		$(xblockElement).find('input[name=submit-button]').removeAttr('disabled');
    	}
  	}


  	function handleShowAnswerResult(result) {
  		console.log('handleShowAnswerResult INVOKED');

  		var teacher_answer = result['generated_answer'];
  		console.log('teacher_answer: ' + teacher_answer);

  		var answer_title_pre_element = $('<pre></pre>');
  		answer_title_pre_element.text('Answer:');

  		var answer_content_prelement = $('<pre></pre>');
  		answer_content_prelement.text(teacher_answer);

  		teacher_answer_div_element.append(answer_title_pre_element);
  		teacher_answer_div_element.append(answer_content_prelement);

  		show_answer_button.attr('disabled', 'disabled');
  	}


  	$(xblockElement).find('input[name=submit-button]').bind('click', function() {
  		// accumulate student's answer for submission

    	var data = {
      		'student_answer': student_answer_textarea_element.val()
    	};

    	console.log('student_answer: ' + data['student_answer']);

        $(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
        $(xblockElement).find('input[name=submit-button]').val("Submitting...")
    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit');
    	$.post(handlerUrl, JSON.stringify(data)).success(handleSubmissionResult);
  	});


    $(function($) {
    	console.log("question_generator_block initialized");
    	if (show_answer_button != null) {
    		show_answer_button.bind('click', function() {
    			console.log("show_answer_button CLICKED");

    			// prepare data
    			var data = {
      				'data': ""
    			}

    			var handlerUrl = runtime.handlerUrl(xblockElement, 'show_answer_handler');
    			$.post(handlerUrl, JSON.stringify(data)).success(handleShowAnswerResult);
    		});
    	}
    });

}