/* Javascript for MatlabQuestionTemplateBuilderXBlock. */
function MatlabQuestionTemplateBuilderXBlock(runtime, xblockElement) {
	"use strict";

//	var hidden_question_template_element = $(xblockElement).find('input[name=question_template]');
//	var hidden_url_image = $(xblockElement).find('input[name=image_url]');
//	var hidden_resolver_selection =$(xblockElement).find('input[name=resolver_selection]');
//	var hidden_variables_element = $(xblockElement).find('input[name=variables]');
//	var hidden_generated_variables_element = $(xblockElement).find('input[name=generated_variables]');
//	var hidden_generated_question_element = $(xblockElement).find('input[name=generated_question]');
//	var hidden_answer_template_element = $(xblockElement).find('input[name=answer_template]');
//  var xblock_id = $(xblockElement).find('input[name=xblock_id]').val();

	var student_answer_textarea_element = $(xblockElement).find('textarea[name=student_answer]');
    var teacher_answer_div_element = $(xblockElement).find('div[name=teacher_answer_div]');
    var show_answer_button = $(xblockElement).find('input[name=show_answer-button]');
    var reset_button = $(xblockElement).find('input[name=reset_problem-button]');
    var action_div = $(xblockElement).find('div.action');


	function handleSubmissionResult(result) {
		console.log('handleSubmissionResult INVOKED');
//		console.log('result:' + JSON.stringify(result));
        action_div.find('span[name=attempt-number]').text(result['attempt_number']);
    	$(xblockElement).find('div[name=problem-progress]').text(result['point_string']);
    	$(xblockElement).find('input[name=submit-button]').val("Submit")

    	if (result['submit_disabled'] == 'disabled') {
    		$(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
    	}
    	else
    	{
    		$(xblockElement).find('input[name=submit-button]').removeAttr('disabled'); 
    	}
  	}
  	
    // Show teacher's answer
  	function handleShowAnswer(result) {
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

  	function clearAnswerView() {
  	    // remove displayed answer
  	    teacher_answer_div_element.find('pre').remove();
  	}

    // This is intent for multiple answers, NOT USED ATM
    // TODO: support multi answers later when required
    function handleShowAnswerResult(result) {
  		console.log('handleShowAnswerResult INVOKED');

        var answers = result['generated_answer'];
        var answer_title_pre_element = $('<pre></pre>');
  		answer_title_pre_element.text('Answer:');
  		teacher_answer_div_element.append(answer_title_pre_element);

        var key;
        for (key in answers) {
            console.log('answer attribute: ' + key);
            console.log('answer value: ' + answers[key]);
            var answer_content_prelement = $('<pre></pre>');
            var answer_string = key + ' = ' + answers[key];
  		    answer_content_prelement.text(answer_string);
            teacher_answer_div_element.append(answer_content_prelement);
        }

        // disable show answer button
  		show_answer_button.attr('disabled', 'disabled');
  	}

    // Update HTML elements when invoked Reset button
  	function handleResetProblem(result) {
		console.log('handleResetProblem INVOKED');
        // update new question
		$(xblockElement).find('div[name=question]').text(result['question']);
//		hidden_generated_question_element.val(result['question'])

//		// update variables
//		hidden_generated_variables_element.val(result['generated_variables']);

//		// update teacher's answer template
//		hidden_answer_template_element.val(result['answer_template']);

		// reset student's answer
		student_answer_textarea_element.val('');

		// update problem progress
		// attempt
        action_div.find('span[name=attempt-number]').text(result['attempt_number']);
        // point
    	$(xblockElement).find('div[name=problem-progress]').text(result['point_string']);

    	// clear shown answer if any
    	clearAnswerView();

    	// Enable Show Answer button if disabled
    	show_answer_button.removeAttr('disabled');

    	// Enable Submit button if disabled
    	$(xblockElement).find('input[name=submit-button]').val("Submit")
    	if (result['submit_disabled'] == 'disabled') {
    		$(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
    	}
    	else
    	{
    		$(xblockElement).find('input[name=submit-button]').removeAttr('disabled');
    	}
  	}


  	$(xblockElement).find('input[name=submit-button]').bind('click', function() {
  		// accumulate student's answer for submission
    	var data = {
//      		'saved_question_template': hidden_question_template_element.val(),
//      		'saved_url_image': hidden_url_image.val(),
//      		'saved_resolver_selection': hidden_resolver_selection.val(),
//      		'saved_answer_template': hidden_answer_template_element.val(),
//      		'serialized_variables': hidden_variables_element.val(),
//      		'serialized_generated_variables': hidden_generated_variables_element.val(),
//      		'saved_generated_question': hidden_generated_question_element.val(),
      		'student_answer': student_answer_textarea_element.val()
    	};

    	console.log('data: ' + data);
    	console.log('student_answer: ' + data['student_answer']);

        $(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
        $(xblockElement).find('input[name=submit-button]').val("Submitting...")

//    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit');
    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit_handler');
    	$.post(handlerUrl, JSON.stringify(data)).success(handleSubmissionResult);
  	});

  	
    $(function($) {
    	console.log("question_generator_block initialized");
//    	Handle show answer
    	if (show_answer_button != null) {
    		show_answer_button.bind('click', function() {
    			console.log("show_answer_button CLICKED");
    			
    			// prepare data
//    			// TODO: retrieve data from backend instead to avoid cheating
//    			var data = {
//      				'saved_question_template': hidden_question_template_element.val(),
//      				'saved_url_image' : hidden_url_image.val(),
//      				'saved_resolver_selection': hidden_resolver_selection.val(),
//      				'saved_answer_template': hidden_answer_template_element. val(),
//		      		'serialized_variables': hidden_variables_element.val(),
//		      		'serialized_generated_variables': hidden_generated_variables_element.val()
//    			}
                var data = {}

                // Convert a JavaScript object into a string with JSON.stringify().
                var data_json = JSON.stringify(data)
    			console.log('JSON data = ' + data_json);

//    			var handlerUrl = runtime.handlerUrl(xblockElement, 'show_answer_handler');
    			var handlerUrl = runtime.handlerUrl(xblockElement, 'get_answer_handler');
//    			$.post(handlerUrl, JSON.stringify(data)).success(handleShowAnswerResult);
    			$.post(handlerUrl, data_json).success(handleShowAnswer);
    		});
    	}

//    	Handle reset problem
    	if (reset_button != null) {
    		reset_button.bind('click', function() {
    			console.log("reset_button CLICKED");

    			// prepare data
    			var data = {}

    			var handlerUrl = runtime.handlerUrl(xblockElement, 'reset_problem_handler');
    			$.post(handlerUrl, JSON.stringify(data)).success(handleResetProblem);
    		});
    	}
    });
  	
}
