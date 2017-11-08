/* Javascript for StudioEditableXBlockMixin. */
function StudioEditableXBlockMixin(runtime, xblockElement) {
    "use strict";

//    console.log(xblockElement);
    var fields = [];
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined'); // Studio includes a copy of tinyMCE and its jQuery plugin
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

    var csxColor = ["#009FE6", "black"];
    var studio_buttons = {
        "parser-tab": "PARSER",
        "template-tab": "TEMPLATE",
        "editor-tab": "EDITOR",
        "settings-tab": "SETTINGS",
    };

    // define tab id mapping of current tab to target tab
    var target_tabId_map = {
        'template-tab' : "editor-tab",
        'editor-tab' : "template-tab"
    };

    // define tab name (heading) for Editor toggle
    var target_tabName_map = {
        'template-tab' : "Simple Template",
        'editor-tab' : "Advanced Editor"
    };

    var error_message_element = $(xblockElement).find('div[name=error-message]');

    // var on TEMPLATE tab
    var question_template_textarea_element = $(xblockElement).find('textarea[name=question_template]');
    var show_question_original_text_textarea_element = $(xblockElement).find('textarea[name=show_question_original_text]');
    var answer_template_textarea_element =  $(xblockElement).find('textarea[name=answer_template]');
    var show_answer_original_text_textarea_element = $(xblockElement).find('textarea[name=show_answer_original_text]');
    // for show / hide question text
    var original_question_text_input_element = $(xblockElement).find('input[name=input_question_text]'); // hidden input
    var original_answer_text_input_element = $(xblockElement).find('input[name=input_answer_text]'); // hidden input
    var question_original_text = original_question_text_input_element.val();
    var answer_original_text = original_answer_text_input_element.val();
    var original_question_text_div_element = $(xblockElement).find('div[name=original_question_text_div]');
    var original_answer_text_div_element = $(xblockElement).find('div[name=original_answer_text_div]');

    var btn_toggle_original_question = $(xblockElement).find('a[name=btn_toggle_original_question]');
    var btn_toggle_original_answer = $(xblockElement).find('a[name=btn_toggle_original_answer]');

    // Image URL
    var url_image_input = $(xblockElement).find('input[name=image_url]');
    // Variables
    var variables_table_element = $(xblockElement).find('table[name=variables_table]');
//    var variables_table_element = $(xblockElement).find('table[id=variables_table]');
    var string_variables_table_element = $(xblockElement).find('table[name=string_variables_table]');


    // for editor mode toggle
    var btn_switch_editor_mode_element = $(xblockElement).find('button[id=btn_switch_editor_mode]');
    var enable_advanced_editor_element = $(xblockElement).find('input[name=enable_advanced_editor]');
    var enable_advanced_editor = enable_advanced_editor_element.val();
    var editor_mode_name_element = $(xblockElement).find('input[name=current_editor_mode_name]');
    var editor_mode_name = editor_mode_name_element.val();

    // for Parser tab
    var show_parser_input_element = $(xblockElement).find('input[name=show_parser]');
    var show_parser_val = show_parser_input_element.val();
    var btn_toggle_parser_text = $(xblockElement).find('input[name=btn_toggle_parser_text]');
    var btn_toggle_parser_element = $(xblockElement).find('button[id=btn_toggle_parser_id]');
    var question_text_element = $(xblockElement).find('textarea[name=question_text]');
    var answer_text_element = $(xblockElement).find('textarea[name=answer_text]');

    // DOM object for xml editor
    var xml_editor_element = $(xblockElement).find('textarea[name=raw_editor_xml_data]');
    var my_XML_Box = '.xml-box';

    // WORKING
    var xml_editor = CodeMirror.fromTextArea($(my_XML_Box)[0], {
        mode: 'xml',
        lineNumbers: true,
        lineWrapping: true
    });

    $(function($) {
        // append tab action bar

//        for (var b in studio_buttons) {
//            $('.editor-modes')
//                .append(
//                    $('<li>', {class: "action-item"}).append(
//                        $('<a />', {class: "action-primary", id: b, text: studio_buttons[b]})
//                    )
//                );
//        }

        // Show question parser tab
        $('.editor-modes')
            .append(
                $('<li>', {class: "action-item"}).append(
                    $('<a />', {class: "action-primary", id: 'parser-tab', text: studio_buttons['parser-tab']})
                )
            );
        // Show template tab
        $('.editor-modes')
            .append(
                $('<li>', {class: "action-item"}).append(
                    $('<a />', {class: "action-primary", id: 'template-tab', text: studio_buttons['template-tab']})
                )
            );
        // Show settings tab
        $('.editor-modes')
            .append(
                $('<li>', {class: "action-item"}).append(
                    $('<a />', {class: "action-primary", id: 'settings-tab', text: studio_buttons['settings-tab']})
                )
            );

        // Set default tab
        var default_tab = 'template-tab';
        // Update default tab
        if(show_parser_val == 'True'){
            default_tab = 'parser-tab';
        } else {
            default_tab = 'template-tab';
            hide_tab('parser-tab');
        };
        // Switch to default tab
        tab_switch(default_tab);

        // Define tabs' click listeners
        $('#parser-tab').click(function() {
            tab_switch("parser-tab");
        });

        $('#template-tab').click(function() {
            tab_switch("template-tab");
        });

        $('#editor-tab').click(function() {
            tab_switch("editor-tab");
        });

        $('#settings-tab').click(function() {
            tab_switch("settings-tab");
        });

        // Handle Advanced/Basic editor toggle
        $('#btn_switch_editor_mode').click(function() {
            // get current tab
            var current_tab = $(this).attr('tab-name');

            if(enable_advanced_editor == 'False') {
                if(! confirmConversionToXml())
                    return;
                // if confirmed, proceed updating editor mode
                enable_advanced_editor = 'True'; // update JS global variable
                enable_advanced_editor_element.val(enable_advanced_editor); // update value to hidden element enable_advanced_editor
            } else {
                if(! confirmConversionToTemplate())
                    return;
                // if confirmed, proceed updating editor mode
                enable_advanced_editor = 'False'; // update global variable
                enable_advanced_editor_element.val(enable_advanced_editor); // update value to hidden input element
            }

            // Update attributes for the current tab <li> tag
            // Update text
            $("#"+current_tab).text(studio_buttons[target_tabId_map[current_tab]]);
            // Update attribute
            $("#"+current_tab).attr('id', target_tabId_map[current_tab]);

            // Update attributes for Editor toggle button
            // Update text
            btn_switch_editor_mode_element.text(target_tabName_map[current_tab]);
            // Update target tab attribute
            btn_switch_editor_mode_element.attr('tab-name', target_tabId_map[current_tab]);

            // targeted editor_mode_name
//            TODO: Check why this cause JS error ???
//            editor_mode_name = target_tabName_map[current_tab]); // update targeted editor_mode_name
////            editor_mode_name = 'Advanced Editor'; // update targeted editor_mode_name
//            editor_mode_name_element.val(editor_mode_name); // update value for hidden element editor_mode_name
//            // update title attribute for the editor mode toggle button
////            $('#btn_switch_editor_mode').attr('title', 'Switch to ' + editor_mode_name + ' mode'); // update title for the Editor mode button
//            $('#btn_switch_editor_mode').title('Switch to ' + editor_mode_name + ' mode'); // update title for the Editor mode button

            // Switch to the targeted tab
            tab_switch(target_tabId_map[current_tab]);

        });

        // Handle Parser toggle
        btn_toggle_parser_element.click(function() {
            // get target tab and action from element's attributes
            var target_tab_id = $(this).attr('tab-name');
            var action = $(this).attr('action');
            var next_action = '';
            var show_this_tab = 'template-tab';

            console.log('action:' + action);
            console.log('show_parser_val:' + show_parser_val);
            console.log('target_tab id:' + target_tab_id);

            if(action == 'show') {
                // update hidden input elems for parser
                show_parser_val = 'True'; // update JS global variable
                show_parser_input_element.val(show_parser_val);
                // Update button's text and action
                btn_toggle_parser_text = 'Hide Parser';
                next_action = 'hide';

                // switch to the targeted tab
                tab_switch(target_tab_id);
                show_tab_heading(target_tab_id);

            } else if(action == 'hide'){
                // update hidden input elems for parser
                show_parser_val = 'False'; // update global variable
                show_parser_input_element.val(show_parser_val);
                // Update button's text and action
                btn_toggle_parser_text = 'Show Parser';
                next_action = 'show';

                // hide the Parser and switch to show_this_tab
                hide_tab(target_tab_id);
                tab_switch(show_this_tab);
            }

            // update text and action attributes for parser toggle button
            btn_toggle_parser_element.text(btn_toggle_parser_text);
            btn_toggle_parser_element.attr('action', next_action);
        });

        // toggle Original Question
        btn_toggle_original_question.bind('click', function(e) {
            console.log("toggle Original Question clicked");
            var action = $(this).attr('action');
            console.log("action = " + action);

            if (action == 'show'){
                // show original question
                showOriginalQuestionText();
                // update toggle element
                btn_toggle_original_question.text('Hide Original Question');
                btn_toggle_original_question.attr('action', 'hide');
            } else {
                // Hide original question
                removeOriginalQuestionText();
                // update toggle element
                btn_toggle_original_question.text('Show Original Question');
                btn_toggle_original_question.attr('action', 'show');
            }
        });

        // toggle Original Answer
        btn_toggle_original_answer.bind('click', function(e) {
            console.log("toggle Original Answer clicked");
            var action = $(this).attr('action');
            console.log("action = " + action);

            if (action == 'show'){
                // show original answer
                showOriginalAnswerText();
                // update toggle element
                btn_toggle_original_answer.text('Hide Original Answer');
                btn_toggle_original_answer.attr('action', 'hide');
            } else {
                // hide original answer
                removeOriginalAnswerText();
                // update toggle element
                btn_toggle_original_answer.text('Show Original Answer');
                btn_toggle_original_answer.attr('action', 'show');
            }
        });

        // listeners for "Remove" buttons of "Variables"
        variables_table_element.find('input[type=button][class=remove_variable_button]').bind('click', function(e) {
        	var removeButton = $(this);
        	var parentRow = removeButton.closest('tr');
        	parentRow.remove();
        });

        // listeners for "Add" buttons of "Variables"
        variables_table_element.find('input[type=button][class=add_variable_button]').bind('click', function(e) {
        	var addButton = $(this);
        	var parentRow = addButton.closest('tr');
        	console.log(parentRow);

            // Insert new variable row after current row
            var current_row_index = $(this).parent().parent().index();
            console.log(current_row_index);
            addVariableRow(current_row_index)

        });

        // listeners for "Remove" buttons of "String Variables"
        string_variables_table_element.find('input[type=button][class=remove_variable_button]').bind('click', function(e) {
        	var removeButton = $(this);
        	var parentRow = removeButton.closest('tr');
        	parentRow.remove();
        });

    });

    // Update highlight
    function tab_highlight(toHighlight) {
        for (var b in studio_buttons) {
            if (b != toHighlight) $("a[id=" + b + "]").css({"color": csxColor[0]});
        }
        $("a[id=" + toHighlight + "]").css({"color": csxColor[1]});
    };

    // Update buttons based on target tab
    function update_buttons(toShow) {
        if (toShow == 'parser-tab') { // tab PARSER
            $("li[name=parse]").show();
            // hide button Add Variable
            $("li[name=add_variable]").hide();
            // hide button Save
            $("li[name=save]").hide();
            // show buttons for Editor and Parser toggle
            btn_switch_editor_mode_element.show();
            // hide Parser toggle
            btn_toggle_parser_element.show();
    	} else if (toShow == 'template-tab') { // tab TEMPLATE
    	    // show Save button
    	    $("li[name=save]").show();
    	    // only show "Add variable" on TEMPLATE tab
    		$("li[name=add_variable]").show();
    		// hide button Parse
    		$("li[name=parse]").hide();
    		// show Editor toggle button
    	    btn_switch_editor_mode_element.show();
    		// show button Show Parser
    		btn_toggle_parser_element.show();
    	} else { // tab SETTINGS
    	    $("li[name=save]").show();
    	    // hide "Add variable"
    		$("li[name=add_variable]").hide();
    		// hide button Parse
    		$("li[name=parse]").hide();
    		// update buttons for Editor and Parser toggle
            btn_switch_editor_mode_element.show();
            btn_toggle_parser_element.hide();
    	}
    };


    // Switch to toShow tab, hide others
    function tab_switch(toShow) {
        // Update highlight
        tab_highlight(toShow);

        // Hide all tabs other than toShow
        for (var b in studio_buttons) $("div[name=" + b + "]").hide();

        // Show toShow tab
        $("div[name=" + toShow + "]").show();

        // Update buttons based on target tab
        update_buttons(toShow);
    };

    // Hide toHide tab
    function hide_tab(toHide) {
        // Hide tab content
        $("div[name="+toHide+"]").hide();

        // Hide tab heading
        hide_tab_heading(toHide);
    };

    // Show toShow tab
    function show_tab(toShow) {
        // Show tab content
        $("div[name="+toShow+"]").show();

        // Show tab heading
        show_tab_heading(toShow);
    };

    function hide_tab_heading(toHide) {
//        console.log($(xblockElement).parent("div").parent("div").parent("div").children(".modal-header"));
        var atag = $(xblockElement).parent("div").parent("div").parent("div").children(".modal-header").find("a[id="+toHide+"]");
        console.log(atag);

        // Hide the <li> headding
        atag.parent('li').css({ "display": 'none'}); // Use the CSS function from jQuery to set styles to <li> headding
//        atag.closest('li').css({ "display": 'none'}); // Use the CSS function from jQuery to set styles to <li> headding
//        atag.closest('li').hide();
    };

    function show_tab_heading(toShow) {
        var atag = $(xblockElement).parent("div").parent("div").parent("div").children(".modal-header").find("a[id="+toShow+"]");
        //console.log(atag);

        // Show the <li> headding
        atag.parent('li').css({ "display": 'inline'}); // Use the CSS function from jQuery to set styles to <li> headding
//        atag.closest('li').css({ "display": 'inline'}); // Use the CSS function from jQuery to set styles to <li> headding
//        atag.closest('li').show();
    };

    // Show original question text
  	function showOriginalQuestionText() {
  		console.log('showOriginalQuestionText INVOKED');
        var original_question_text = original_question_text_input_element.val();
  		console.log('original_question_text: ' + original_question_text);

  		var original_question_text_title_element = $('<h6></h6>');
  		original_question_text_title_element.text('Original Question:');
  		original_question_text_title_element.css('font-weight', 'bold');

//  		var original_question_text_content_element = $('<pre></pre>');
        var original_question_text_content_element = $('<textarea name="show_question_original_text" rows=10 cols=80></textarea>');
  		original_question_text_content_element.val(original_question_text);

  		original_question_text_div_element.append(original_question_text_title_element);
  		original_question_text_div_element.append(original_question_text_content_element);
  	};

  	function removeOriginalQuestionText() {
  	    // remove displayed question text
  	    original_question_text_div_element.find('h6').hide();
  	    original_question_text_div_element.find('textarea').hide();
  	};

  	// Show original answer text
  	function showOriginalAnswerText() {
  		console.log('showOriginalAnswerText() INVOKED');
        var original_answer_text = original_answer_text_input_element.val();
  		console.log('Original answer: ' + original_answer_text);

  		var original_answer_text_title_element = $('<h6></h6>');
  		original_answer_text_title_element.text('Original Answer:');
  		original_answer_text_title_element.css('font-weight', 'bold');

//  		var original_answer_text_content_element = $('<pre></pre>');
        var original_answer_text_content_element = $('<textarea name="show_answer_original_text" rows=5 cols=80></textarea>');
  		original_answer_text_content_element.text(original_answer_text);

  		original_answer_text_div_element.append(original_answer_text_title_element);
  		original_answer_text_div_element.append(original_answer_text_content_element);
  	};

  	function removeOriginalAnswerText() {
  	    // remove displayed question text
  	    original_answer_text_div_element.find('h6').hide();
        original_answer_text_div_element.find('textarea').hide();
  	};

    function addVariableRow(current_row_index) {
    	console.log("function addVariableRow() invoked");

    	var new_row = $('<tr></tr>');
    	new_row.attr("class", "formula_edit_table_row");

    	// 1st column: variable name
    	var first_column = $('<td></td>');
    	first_column.addClass("table_cell_alignment first_column");
    	var variable_name_element = $('<input />');
    	variable_name_element.attr("type", "text");
    	variable_name_element.attr("class", "formula_input_text");
    	variable_name_element.attr("value", "");
    	// Append element to column
    	first_column.append(variable_name_element);
    	// Append column to row
    	new_row.append(first_column);

    	// 2nd column: Original text
    	var second_column = $('<td></td>');
    	second_column.addClass("table_cell_alignment number_input_cell");
    	var original_text_element = $('<input />');
    	original_text_element.attr("type", "text");
    	original_text_element.attr("class", "formula_input_text");
    	original_text_element.attr("value", "");
    	// Append element to column
    	second_column.append(original_text_element);
    	// Append column to row
    	new_row.append(second_column);

    	// 3rd column: Variable Type
    	var third_column  = $('<td></td>');
    	third_column.attr("class", "table_cell_alignment");
    	var variable_type_element = $('<select></select>');
    	variable_type_element.attr("class", "variable_type");
    	// Int option
    	var int_option_element = $("<option></option>");
    	int_option_element.attr("value", "int");
    	int_option_element.text("Int");
    	int_option_element.attr("selected", "selected");
    	variable_type_element.append(int_option_element);
    	// Float option
    	var float_option_element = $("<option></option>");
    	float_option_element.attr("value", "float");
    	float_option_element.text("Float");
    	variable_type_element.append(float_option_element);
    	// Custom value option
    	var custom_option_element = $("<option></option>");
    	custom_option_element.attr("value", "custom");
    	custom_option_element.text("Custom values");
    	variable_type_element.append(custom_option_element);
    	// Append element to column
    	third_column.append(variable_type_element);
    	// Append column to row
    	new_row.append(third_column);

    	// 4th column: min value
    	var fourth_column  = $('<td></td>');
    	fourth_column.attr("class", "table_cell_alignment number_input_cell");
    	var variable_min_value_element = $('<input />');
    	variable_min_value_element.attr("type", "number");
    	variable_min_value_element.attr("class", "formula_input_text");
    	variable_min_value_element.attr("value", "1");
    	// Append element to column
    	fourth_column.append(variable_min_value_element);
    	// Append column to row
    	new_row.append(fourth_column);

    	// 5th column: max value
    	var fith_column  = $('<td></td>');
    	fith_column.attr("class", "table_cell_alignment number_input_cell");

    	var variable_max_value_element = $('<input />');
    	variable_max_value_element.attr("type", "number");
    	variable_max_value_element.attr("class", "formula_input_text");
    	variable_max_value_element.attr("value", "10");
    	// Append element to column
    	fith_column.append(variable_max_value_element);
    	// Append column to row
    	new_row.append(fith_column);

    	// 6th column: decimal_places
    	var sixth_column  = $('<td></td>');
    	sixth_column.attr("class", "table_cell_alignment number_input_cell");
    	var variable_decimal_places_element = $('<input>');
    	variable_decimal_places_element.attr("type", "number");
    	variable_decimal_places_element.attr("min", "0");
    	variable_decimal_places_element.attr("max", "7");
    	variable_decimal_places_element.attr("class", "formula_input_text");
    	variable_decimal_places_element.attr("value", "0");
    	// Append element to column
    	sixth_column.append(variable_decimal_places_element);
    	// Append column to row
    	new_row.append(sixth_column);

    	// 7th column: Remove button
    	var seventh_column  = $('<td></td>');
    	seventh_column.attr("class", "table_cell_alignment button_cell");
    	var remove_variable_button = $('<input>');
    	remove_variable_button.attr("type", "button");
    	remove_variable_button.addClass("remove_variable_button");
    	remove_variable_button.attr("value", "x");
    	// Append element to column
    	seventh_column.append(remove_variable_button);
    	// Append column to row
    	new_row.append(seventh_column);

        // 8th column: Add button
    	var eighth_column  = $('<td></td>');
    	eighth_column.attr("class", "table_cell_alignment button_cell last_column");
    	var add_variable_button = $('<input>');
    	add_variable_button.attr("type", "button");
    	add_variable_button.addClass("add_variable_button");
    	add_variable_button.attr("value", "+");
    	// Append element to column
    	eighth_column.append(add_variable_button);
    	// Append column to row
    	new_row.append(eighth_column);

    	//    	// Finally, append the new row to the table
//    	variables_table_element.append(new_row);

        // Insert new row after current row
        console.log('current row index = ' + current_row_index);
    	$('#variables_table > tbody > tr').eq(current_row_index).after(new_row);

    	// Add event listener for Remove button click
    	remove_variable_button.click(function() {
    		new_row.remove();
    	});

    	// listeners for "Add" buttons of "Variables"
        variables_table_element.find('input[type=button][class=add_variable_button]').bind('click', function(e) {
        	var addButton = $(this);
        	var parentRow = addButton.closest('tr');
        	console.log(parentRow);

            // Insert new variable row after current row
            var current_row_index = $(this).parent().parent().index();
            console.log(current_row_index);
            addVariableRow(current_row_index)

        });

    };

    /*
     Have the user confirm the one-way conversion to XML.
     Returns true if the user clicked OK, else false.
     */
    function confirmConversionToXml() {
        return confirm(gettext('If you switch to the Advanced Editor, the TEMPLATE tab will be replaced by an XML Editor for raw edit the problem. You can toggle back and forth between Simple Template and Advanced Editor anytime.\n\nProceed to the Advanced Editor?')); // eslint-disable-line max-len, no-alert
    };

    /*
     Have the user confirm the one-way conversion to XML.
     Returns true if the user clicked OK, else false.
     */
    function confirmConversionToTemplate() {
        return confirm(gettext('Are you sure you want to switch back to the Simple Template interface. You can toggle back and forth between Simple Template and Advanced Editor anytime.\n\nProceed ?')); // eslint-disable-line max-len, no-alert
    };


   function fillErrorMessage(errorMessage) {
		error_message_element.empty();

		if (errorMessage != null) {
			var errorLabelNode = "<label class='validation_error'>" + errorMessage + "</label>";
			error_message_element.append(errorLabelNode);
		}
    }

    $(xblockElement).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean')
                    return (val == 'true' || val == '1');
                if (type == "integer")
                    return parseInt(val, 10);
                if (type == "float")
                    return parseFloat(val);
                if (type == "generic" || type == "list" || type == "set") {
                    val = val.trim();
                    if (val === "")
                        val = null;
                    else
                        val = JSON.parse(val); // TODO: handle parse errors
                }
                return val;
            },
            removeEditor: function() {
                $field.tinymce().remove();
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        
        $field.bind("change input paste", fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });

        if (type == 'datepicker' && datepickerAvailable) { // TODO remove?
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: "m/d/yy"});
        }
    });


    $(xblockElement).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');

        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return false; },
            val: function() {
                var val = [];
                $checkboxes.each(function() {
                    if ($(this).is(':checked')) {
                        val.push(JSON.parse($(this).val()));
                    }
                });
                return val;
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $checkboxes.bind("change input", fieldChanged);

        $resetButton.click(function() {
            var defaults = JSON.parse($wrapper.attr('data-default'));
            $checkboxes.each(function() {
                var val = JSON.parse($(this).val());
                $(this).prop('checked', defaults.indexOf(val) > -1);
            });
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
    });

    var studioSubmit = function(data) {
        var handlerUrl = runtime.handlerUrl(xblockElement, 'fe_submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    // Save action
    $(xblockElement).find('a[name=save_button]').bind('click', function(e) {
    	console.log("Save button clicked");

    	// Reset error message if have
    	error_message_element.empty();
    	
    	// Handle "SETTINGS" tab
        e.preventDefault();
        var fieldValues = {};
        var fieldValuesNotSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
            if (field.isSet()) {
                fieldValues[field.name] = field.val();
            } else {
                fieldValuesNotSet.push(field.name);
            }
            // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
            // when loading editor for another block:
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }

        // 1. Handle xml_editor element
        var raw_editor_xml_data = xml_editor.getValue();
        //console.log('raw_editor_xml_data: ' + raw_editor_xml_data);
        
        /*
        Handle "TEMPLATE" tab
			1. question_template
			2. answer_template
			3. Image URL
			4. variables (name, min_valua, max_value, type, decimal_places)

        */
        // 1.1: Get question template from question_template_textarea_element
        var question_template = question_template_textarea_element.val();
        console.log('question_template: ' + question_template);

        // 2.1 answer_template
        var answer_template = answer_template_textarea_element.val();
        console.log('answer_template: ' + answer_template);

        // 3: image
        var image_url = url_image_input.val();

        // 4.1: Handle string variables
        // Get values from string variables table element
        var string_variables = []
        string_variables_table_element.find('tr').each(function(row_index)
        {
            if (row_index > 0)
            {
                var variable = {};
                var columns = $(this).find('td');
                var variable_name = columns.eq(0).children().eq(0).val();
                var context = columns.eq(2).children().eq(0).val();
                var value = columns.eq(3).children().eq(0).val();
                variable['name'] = variable_name;
                variable['context'] = context;
                variable['value'] = value;

                // add to string variable list
                string_variables.push(variable);
            }        
        });
//        console.log("string varirables: " + string_variables);

        // 4.2: Handle numeric variables
        // Get values from variables_table_element
        var variables = {};
    	variables_table_element.find('tr').each(function(row_index) {
    		if (row_index > 0) { // first row is the table header
    			var variable = {}
    			var columns = $(this).find('td');
    			
    			// 1st column: "variable name"
                var variable_name = columns.eq(0).children().eq(0).val();
    			if (variable_name.length == 0) { // empty variable name
    				fillErrorMessage('Variable name can not be empty');
    				return false;
    			}
//    			console.log('variable_name = ' + variable_name);
//    			console.log('variables dict = ' + JSON.stringify(variables));
    			if (variables.hasOwnProperty(variable_name)) { // duplicate verification
    				fillErrorMessage('Variable name can not be duplicated');
    				return false;
    			}
    			variable['name'] = variable_name;

    			// 2nd column: "original_text"
                var original_text = columns.eq(1).children().eq(0).val();
    			if (original_text.length == 0) { // check empty
    				fillErrorMessage('Original text shall not be empty');
    				return false;
    			}
    			if (variables.hasOwnProperty(original_text)) { // duplicate verification
    				fillErrorMessage('Original text shall not be empty');
    				return false;
    			}
    			variable['original_text'] = original_text;

    			// 3rd column: "type"
    			var type = columns.eq(2).children().eq(0).val();
    			variable['type'] = type;

    			// 4th column: "min_value"
    			var min_value = columns.eq(3).children().eq(0).val();
    			if (min_value.length == 0) { // empty min_value
    				fillErrorMessage('min_value can not be empty');
    				return false;
    			}
    			variable['min_value'] = min_value;

    			// 5th column: "max_value"
    			var max_value = columns.eq(4).children().eq(0).val();
    			if (max_value.length == 0) { // empty max_value
    				fillErrorMessage('max_value can not be empty');
    				return false;
    			}
    			var min_value_numer = Number(min_value);
    			var max_value_number = Number(max_value);
    			if (min_value_numer > max_value_number) {
    				fillErrorMessage('min_value can not be bigger than max_value');
    				return false;
    			}
    			variable['max_value'] = max_value;
    			
    			// 6th column: "decimal_places"
    			var decimal_places = columns.eq(5).children().eq(0).val();
    			variable['decimal_places'] = decimal_places;
    			
    			variables[variable_name] = variable;
    			console.log('Row ' + row_index + ': variable_name: ' + variable_name + ', min: ' + min_value + ', max: ' + max_value + ', type: ' + type + ', decimal_places: ' + decimal_places);
    		}
    	});
    	
        // Client-side validation error
        if (error_message_element.children().length > 0) { 
        	return;
        }

        var submit_data = {
                            enable_advanced_editor: enable_advanced_editor,
                            values: fieldValues,
                            defaults: fieldValuesNotSet,
                            question_template: question_template,
                            image_url: image_url,
                            variables: variables,
                            answer_template: answer_template,
                            raw_editor_xml_data: raw_editor_xml_data,
                            string_variables: string_variables
                            };

        /*
        HANDLE ORIGINAL TEXT UPDATE
        */
        // 1.2: Get question original text if shown from question_original_text_textarea_element
        // Relocate the element to get its updated value
        show_question_original_text_textarea_element = $(xblockElement).find('textarea[name=show_question_original_text]');
        if(show_question_original_text_textarea_element.length > 0){ // element found
            var updated_question_original_text = show_question_original_text_textarea_element.val();

            // Check if show_question_original_text_textarea_element found and its value changed,
            // Add the updated value into submit_data for studio edit submission
            console.log('question_original_text = ' + question_original_text);
            console.log('updated_question_original_text = ' + updated_question_original_text);
            if(updated_question_original_text !== undefined && updated_question_original_text != question_original_text){
                submit_data['updated_question_original_text'] = updated_question_original_text;

                // Update newly value from textarea back to hidden input element
                original_question_text_input_element.val(updated_question_original_text);
            }
        }

        // 2.2: Get answer original text if shown from answer_original_text_textarea_element
        // Relocate the element to get its updated value
        show_answer_original_text_textarea_element = $(xblockElement).find('textarea[name=show_answer_original_text]');
        if(show_answer_original_text_textarea_element.length > 0){ // element found
            var updated_answer_original_text = show_answer_original_text_textarea_element.val();

            // Check if show_answer_original_text_textarea_element found and its value changed,
            // Add the updated value into submit_data for studio edit submission
            console.log('answer_original_text = ' + answer_original_text);
            console.log('updated_answer_original_text: ' + updated_answer_original_text);
            if(updated_answer_original_text !== undefined && updated_answer_original_text != answer_original_text){
                submit_data['updated_answer_original_text'] = updated_answer_original_text;

                // Update newly value from textarea back to hidden input element
                original_answer_text_input_element.val(updated_answer_original_text);
            }
        }
        console.log(submit_data);

        // Server side validation
        // perform save action submit and update default editor mode
	    studioSubmit(submit_data);
    });


    /*
    * Handle parse question text (Cont.)
    * Server side processing
    */
    var studioPasreQuestion = function(data) {
        var handlerUrl = runtime.handlerUrl(xblockElement, 'fe_parse_question_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Parsing text ...")});

        var data_json = JSON.stringify(data);
        console.log(data_json);

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: data_json,
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    /*
    * Handle parse button click
    * collect data, pass to backend validation
    */
    $(xblockElement).find('a[name=parse_button]').bind('click', function(e) {
    	console.log("Parse button clicked");
        // Empty error message element
    	error_message_element.empty();

        // Get question text fields
        var q = question_text_element.val();
        var a = answer_text_element.val();

        if (q.length == 0) { // check if empty question
                fillErrorMessage('Question can not be empty!');
                return false;
        }

        if (a.length == 0) { // check if empty answer
                fillErrorMessage('Answer can not be empty!');
                return false;
        }

        // Client-side error validation
        if (error_message_element.children().length > 0) {
        	return;
        }

        var data = {
                        original_question: q,
                        original_answer: a
                   };

        // Server side validation
	    studioPasreQuestion(data);
    });


    $(xblockElement).find('.cancel-button').bind('click', function(e) {
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        for (var i in fields) {
            var field = fields[i];
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        e.preventDefault();
        runtime.notify('cancel', {});
    });
    
    
//    $(xblockElement).find('input[name=add_variable_button]').bind('click', function(e) {
//    	console.log("Add VARIABLE button clicked");
//
//    	var new_row = $('<tr></tr>');
//    	new_row.attr("class", "formula_edit_table_row");
//
//    	// 1st column: variable name
//    	var first_column = $('<td></td>');
//    	first_column.attr("class", "table_cell_alignment");
//    	var variable_name_element = $('<input />');
//    	variable_name_element.attr("type", "text");
//    	variable_name_element.attr("class", "formula_input_text");
//    	variable_name_element.attr("value", "");
//    	// Append element to column
//    	first_column.append(variable_name_element);
//    	// Append column to row
//    	new_row.append(first_column);
//
//    	// 2nd column: Original text
//    	var second_column = $('<td></td>');
//    	second_column.attr("class", "table_cell_alignment");
//    	var original_text_element = $('<input />');
//    	original_text_element.attr("type", "text");
//    	original_text_element.attr("class", "formula_input_text");
//    	original_text_element.attr("value", "");
//    	// Append element to column
//    	second_column.append(original_text_element);
//    	// Append column to row
//    	new_row.append(second_column);
//
//    	// 3rd column: Variable Type
//    	var third_column  = $('<td></td>');
//    	third_column.attr("class", "table_cell_alignment");
//    	var variable_type_element = $('<select></select>');
//    	variable_type_element.attr("class", "variable_type");
//    	// Int option
//    	var int_option_element = $("<option></option>");
//    	int_option_element.attr("value", "int");
//    	int_option_element.text("Int");
//    	int_option_element.attr("selected", "selected");
//    	variable_type_element.append(int_option_element);
//    	// Float option
//    	var float_option_element = $("<option></option>");
//    	float_option_element.attr("value", "float");
//    	float_option_element.text("Float");
//    	variable_type_element.append(float_option_element);
//    	// Custom value option
//    	var custom_option_element = $("<option></option>");
//    	custom_option_element.attr("value", "custom");
//    	custom_option_element.text("Custom values");
//    	variable_type_element.append(custom_option_element);
//    	// Append element to column
//    	third_column.append(variable_type_element);
//    	// Append column to row
//    	new_row.append(third_column);
//
//    	// 4th column: min value
//    	var fourth_column  = $('<td></td>');
//    	fourth_column.attr("class", "table_cell_alignment number_input_cell");
//    	var variable_min_value_element = $('<input />');
//    	variable_min_value_element.attr("type", "number");
//    	variable_min_value_element.attr("class", "formula_input_text");
//    	variable_min_value_element.attr("value", "1");
//    	// Append element to column
//    	fourth_column.append(variable_min_value_element);
//    	// Append column to row
//    	new_row.append(fourth_column);
//
//    	// 5th column: max value
//    	var fith_column  = $('<td></td>');
//    	fith_column.attr("class", "table_cell_alignment number_input_cell");
//
//    	var variable_max_value_element = $('<input />');
//    	variable_max_value_element.attr("type", "number");
//    	variable_max_value_element.attr("class", "formula_input_text");
//    	variable_max_value_element.attr("value", "10");
//    	// Append element to column
//    	fith_column.append(variable_max_value_element);
//    	// Append column to row
//    	new_row.append(fith_column);
//
//    	// 6th column: decimal_places
//    	var sixth_column  = $('<td></td>');
//    	sixth_column.attr("class", "table_cell_alignment number_input_cell");
//    	var variable_decimal_places_element = $('<input>');
//    	variable_decimal_places_element.attr("type", "number");
//    	variable_decimal_places_element.attr("min", "0");
//    	variable_decimal_places_element.attr("max", "7");
//    	variable_decimal_places_element.attr("class", "formula_input_text");
//    	variable_decimal_places_element.attr("value", "0");
//    	// Append element to column
//    	sixth_column.append(variable_decimal_places_element);
//    	// Append column to row
//    	new_row.append(sixth_column);
//
//    	// 7th column: Remove button
//    	var seventh_column  = $('<td></td>');
//    	seventh_column.attr("class", "table_cell_alignment");
//    	var remove_variable_button = $('<input>');
//    	remove_variable_button.attr("type", "button");
////    	remove_variable_button.attr("class", "remove_variable_button");
//    	remove_variable_button.addClass("remove_variable_button");
//    	remove_variable_button.addClass("remove_button");
//    	remove_variable_button.attr("value", "Remove");
//    	// Append element to column
//    	seventh_column.append(remove_variable_button);
//    	// Append column to row
//    	new_row.append(seventh_column);
//
//    	// Add event listener for Remove button click
//    	remove_variable_button.click(function() {
//    		new_row.remove();
//    	});
//
//    	// Finally, append the new row to the table
//    	variables_table_element.append(new_row);
//
//    });

//    $(document).ready(function() {
//        var variable_type_select = $(xblockElement).find('.variable_type');
//
//        // Handle variable type select, generate HTML elements based on input
//        variable_type_select.change(function(e) {
//            console.log("Variable Type option changed");
//
//            // Get current row
//            var new_row = $this.closest('tr');
//
//            // 3rd column: Type
//            var third_column  = $('<td></td>');
//            third_column.attr("class", "table_cell_alignment");
//            var variable_type_element = $('<select></select>');
//            variable_type_element.attr("class", "formula_input_text");
//            // Int option
//            var int_option_element = $("<option></option>");
//            int_option_element.attr("value", "int");
//            int_option_element.text("Int");
//            int_option_element.attr("selected", "selected");
//            variable_type_element.append(int_option_element);
//            // Float option
//            var float_option_element = $("<option></option>");
//            float_option_element.attr("value", "float");
//            float_option_element.text("Float");
//            variable_type_element.append(float_option_element);
//            // Custom value option
//            var custom_option_element = $("<option></option>");
//            custom_option_element.attr("value", "custom");
//            custom_option_element.text("Custom values");
//            variable_type_element.append(custom_option_element);
//            // Append element to column
//            third_column.append(variable_type_element);
//            // Append column to row
//            new_row.append(third_column);
//
//            // 4th column: min value
//            var fourth_column  = $('<td></td>');
//            fourth_column.attr("class", "table_cell_alignment number_input_cell");
//            var variable_min_value_element = $('<input />');
//            variable_min_value_element.attr("type", "number");
//            variable_min_value_element.attr("class", "formula_input_text");
//            variable_min_value_element.attr("value", "1");
//            // Append element to column
//            fourth_column.append(variable_min_value_element);
//            // Append column to row
//            new_row.append(fourth_column);
//
//            // 5th column: max value
//            var fith_column  = $('<td></td>');
//            fith_column.attr("class", "table_cell_alignment number_input_cell");
//            var variable_max_value_element = $('<input />');
//            variable_max_value_element.attr("type", "number");
//            variable_max_value_element.attr("class", "formula_input_text");
//            variable_max_value_element.attr("value", "10");
//            // Append element to column
//            fith_column.append(variable_max_value_element);
//            // Append column to row
//            new_row.append(fith_column);
//
//            // 6th column: decimal_places
//            var sixth_column  = $('<td></td>');
//            sixth_column.attr("class", "table_cell_alignment number_input_cell");
//            var variable_decimal_places_element = $('<input>');
//            variable_decimal_places_element.attr("type", "number");
//            variable_decimal_places_element.attr("min", "0");
//            variable_decimal_places_element.attr("max", "7");
//            variable_decimal_places_element.attr("class", "formula_input_text");
//            variable_decimal_places_element.attr("value", "0");
//            // Append element to column
//            sixth_column.append(variable_decimal_places_element);
//            // Append column to row
//            new_row.append(sixth_column);
//
//            // 7th column: Remove button
//            var seventh_column  = $('<td></td>');
//            seventh_column.attr("class", "table_cell_alignment");
//            var remove_variable_button = $('<input>');
//            remove_variable_button.attr("type", "button");
//    //    	remove_variable_button.attr("class", "remove_variable_button");
//            remove_variable_button.addClass("remove_variable_button");
//            remove_variable_button.addClass("remove_button");
//            remove_variable_button.attr("value", "Remove");
//            // Append element to column
//            seventh_column.append(remove_variable_button);
//            // Append column to row
//            new_row.append(seventh_column);
//
//            // Add event listener for Remove button click
//            remove_variable_button.click(function() {
//                new_row.remove();
//            });
//
//            // Finally, append the new row to the table
//            variables_table_element.append(new_row);
//        });
//
//    });
    
}
