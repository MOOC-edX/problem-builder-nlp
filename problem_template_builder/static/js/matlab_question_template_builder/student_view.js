/* Javascript for MathProblemTemplateBuilderXBlock. */
function MathProblemTemplateBuilderXBlock(runtime, xblockElement) {
	"use strict";

	var student_answer_textarea_element = $(xblockElement).find('textarea[name=student_answer]');
    var teacher_answer_div_element = $(xblockElement).find('div[name=teacher_answer_div]');
    var show_answer_button = $(xblockElement).find('input[name=show_answer-button]');
    var reset_button = $(xblockElement).find('input[name=reset_problem-button]');
    var action_div = $(xblockElement).find('div.action');

    /*
    * Update Submission Result View
    */
	function updateSubmissionResultView(result) {
		console.log('updateSubmissionResultView INVOKED');
        // Update result to Student view
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
  	
    /*
    * Show problem answer (teacher's answer)
    */
  	function updateShowAnswerView(result) {
  		console.log('updateShowAnswerView INVOKED');

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

    /*
    * Remove shown answer
    */
  	function removeAnswerView() {
  	    teacher_answer_div_element.find('pre').remove();
  	}

    /*
    * Update HTML elements when invoked Reset button
    */
  	function updateResetProblemView(result) {
		console.log('updateResetProblemView INVOKED');
        // update new question
		$(xblockElement).find('div[name=question]').text(result['question']);

		// reset student's answer
		student_answer_textarea_element.val('');

		// update problem progress
		// attempt
        action_div.find('span[name=attempt-number]').text(result['attempt_number']);
        // point
    	$(xblockElement).find('div[name=problem-progress]').text(result['point_string']);

    	// Remove previous shown answer if have
    	removeAnswerView();

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

    /*
    * AJAX function handle answer submission from Student view
    */
  	$(xblockElement).find('input[name=submit-button]').bind('click', function() {
  		// Get student's answer for submission
    	var data = {
      		'student_answer': student_answer_textarea_element.val()
    	};
    	console.log(data);
        // Update the display of button
        $(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
        $(xblockElement).find('input[name=submit-button]').val("Submitting...")

    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit_handler');
    	$.post(handlerUrl, JSON.stringify(data)).success(updateSubmissionResultView);
  	});

  	
    $(function($) {
    	console.log("NLTK Math xBlock initialized");
    	/*
        * AJAX function handle Show Answer button click
        */
    	if (show_answer_button != null) {
    		show_answer_button.bind('click', function() {
    			console.log("show_answer_button CLICKED");
    			
                var data = {}
                // Convert a JavaScript object into a string with JSON.stringify().
                var data_json = JSON.stringify(data)

                // TODO: now get problem answer from backend instead of hidden inputs,
                // this is to avoid cheating by inpecting HTML elements
    			var handlerUrl = runtime.handlerUrl(xblockElement, 'get_answer_handler');
    			$.post(handlerUrl, data_json).success(updateShowAnswerView);
    		});
    	}

        /*
        * Handle problem reset
        */
    	if (reset_button != null) {
    		reset_button.bind('click', function() {
    			console.log("reset_button CLICKED");

    			// pass empty data to backkend handler
    			var data_json = JSON.stringify({});

    			var handlerUrl = runtime.handlerUrl(xblockElement, 'reset_problem_handler');
    			$.post(handlerUrl, data_json).success(updateResetProblemView);
    		});
    	}
    });

    /*
    * This is intent for multiple answers, NOT USED ATM
    * TODO: support multi answers later when required
    */
//    function handleShowAnswerResult(result) {
//  		console.log('handleShowAnswerResult INVOKED');
//
//        var answers = result['generated_answer'];
//        var answer_title_pre_element = $('<pre></pre>');
//  		answer_title_pre_element.text('Answer:');
//  		teacher_answer_div_element.append(answer_title_pre_element);
//
//        var key;
//        for (key in answers) {
//            console.log('answer attribute: ' + key);
//            console.log('answer value: ' + answers[key]);
//            var answer_content_prelement = $('<pre></pre>');
//            var answer_string = key + ' = ' + answers[key];
//  		    answer_content_prelement.text(answer_string);
//            teacher_answer_div_element.append(answer_content_prelement);
//        }
//
//        // disable show answer button
//  		show_answer_button.attr('disabled', 'disabled');
//  	}
  	
}
