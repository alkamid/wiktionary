// http://blog.dobryslownik.pl/po-co-przyklady-uzycia-w-slowniku/

var css = [
    '#wikiEditor-ui-examples {display: block; height=10px; background-color: #eeeedd;}',
    '.toggle-button { background-color: white; margin: 5px 0; border: 2px solid #D0D0D0; height: 24px; width: 100px; cursor:pointer; position: relative; display: inline-block; user-select: none; -webkit-user-select: none; -ms-user-select: none; -moz-user-select: none; text-align: center; }',
    '.toggle-button-selected-good { background-color: #83B152; border: 2px solid #7DA652; }',
    '.toggle-button-selected-bad { background-color: #e34a33; border: 2px solid #ca331c; }',
    '.example-div {display: none;}',
    '.example-box {display: inline-block; width:100%;}',
    '.raw-text {width:50%; float:left;}',
    '.left-context {font-size: x-small;}',
    '.wikified-text {width:50%; float:left;}',
    '.raw-textarea {resize: vertical;}',
    '.source {font-size: small}',
    '.selector-div-unknown-choice {color: red; font-weight: bold;}',
    '.current {display: block;}'
];


// Make sure the utilities module is loaded (will only load if not already)
mw.loader.using( 'mediawiki.util', function () {

    var config = mw.config.get( [
	'wgTitle',
	'wgNamespaceNumber',
	'wgAction',
	'wgCurRevisionId',
	'wgUserName'
    ] );

var verifyButtonAction = function(content, good_or_bad) {
    return function(event) {
	var $thisbutton = $('.current.example-div').find('.toggle-button.' + good_or_bad + '-button');
	var $thatbutton = $('.current.example-div').find(':not(.toggle-button.' + good_or_bad + '-button)'); 
	var $selectordiv = $('.current.example-div').find('.def-selector');

	selectorValue = $selectordiv.find('.num_selector').val();
	if (good_or_bad == 'good' && selectorValue === '') {
    	    $selectordiv.addClass('selector-div-unknown-choice');
	    return -1;
	}

	$selectordiv.removeClass('selector-div-unknown-choice');
	
	$thisbutton.toggleClass('toggle-button-selected-' + good_or_bad);
	$thatbutton.removeClass('toggle-button-selected-' + (good_or_bad === 'good' ? 'bad' : 'good'));
	
	index = $thisbutton.attr('data-index');
	
	if (good_or_bad === 'good') {
	    if (content[index].good_example === true) {
    	 	content[index].verificator = 'None';
    	 	content[index].correct_num = 'None';
    	    }
    	    else if (content[index].bad_example === true) {
    	 	content[index].bad_example = false;
    	 	content[index].correct_num = $('.num_selector').eq(index).find(":selected").text();
    	    }
    	    else {
    	 	content[index].verificator = config.wgUserName;
    	 	content[index].correct_num = $('.num_selector').eq(index).find(":selected").text();
    	    }
    	    content[index].good_example = !content[index].good_example;
    	}
	else if (good_or_bad === 'bad') {
	    if (content[index].bad_example === true) {
    	 	content[index].verificator = 'None';
    	 	content[index].correct_num = 'None';
    	    }
    	    else if (content[index].good_example === true) {
    	 	content[index].good_example = false;
    	 	content[index].correct_num = 'None';
    	    }
    	    else {
    	 	content[index].verificator = config.wgUserName;
    	    }
       	    content[index].bad_example = !content[index].bad_example;
	}
	document.editform.wpTextbox1.value = JSON.stringify(content, null, 4);
	
    };
};
    
    // mw.loader.load( '//rawgit.com/jeresig/jquery.hotkeys/master/jquery.hotkeys.js' );
    /*TODO: <thedj> alkamid: usually, check if the external library is defined if you want to use it, and be prepared for it not being defined and you having to 'reschedule' another attempt to do you 'setup' at a later time, is the strategy often followed in this case.*/

    // Wait for the page to be parsed
    $(document).ready( function () { 

	// This script is intended for pages generated by AlkamidBot only
        if (config.wgTitle === 'Przykłady' && config.wgAction == 'edit') {
            
	    // Content written by AlkamidBot is in JSON format
            var content = $.parseJSON(document.editform.wpTextbox1.value);
	    
	    // This is the main edit div for usage examples
	    var $editbox = $('<div>')
        	.attr('id', 'wikiEditor-ui-examples')
		.prependTo($('.wikiEditor-ui-bottom'));
            
	    $.each(content, function(index, word) {
		
		// for each word, a div is created - only one is set as "current" at a time,
		// and the other ones are hidden
		$singleExampleDiv = $('<div>')
		    .addClass('example-div')
		    .appendTo($editbox);
		

		// title in bold
		$singleExampleDiv
		    .append($('<p>')
			    .append($('<b>').text(word.title))
			   );
		
		// at the beginning, show only the first word
		if (index === 0) {
		    $singleExampleDiv.addClass('first current');
		}

		// this class is important for deactivating the "next" button
		if (index === content.length -1) {
		    $singleExampleDiv.addClass('last');
		}
		
		// container for definitions
		$defdiv = $('<div>')
		    .addClass('defs-div')
		    .appendTo($singleExampleDiv);
		
		// containter for example text
		$textdiv = $('<div>')
		    .addClass('example-box')
		    .appendTo($singleExampleDiv);

		// container for raw text ([[such]] [[as]] [[this]])
		$rawTextdiv = $('<div>')
		    .addClass('raw-text')
		    .appendTo($textdiv);

		// left context - in case the usage is not clear from what's been copied into the textbox
		$leftcontext = $('<p>')
		    .addClass('left-context')
		    .text(word.left_extra)
		    .appendTo($rawTextdiv);

		// refresh button - I put it in another diff for it to stay in one place
		$refreshDiv= $('<div>')
		    .addClass('wikified-text')
		    .appendTo($textdiv);
		
		$reloadButton = $('<button>')
		    .text('odśwież')
		    .appendTo($refreshDiv);

		$reloadButton.click(function(){
		    event.preventDefault();
		    $('#wikified-text' + index).empty();
		    wikifyExample($('#wikified-text' + index), $('#textarea' + index).val());
		        
		});

		// wikified text - can be refreshed
		$wikifiedTextdiv = $('<div>')
		    .addClass('wikified-text')
		    .attr('id', 'wikified-text' + index)
		    .appendTo($textdiv);

		wikifyExample($wikifiedTextdiv, word.example);

		// editable wikitext
		$rawTextdiv
		    .append($('<textarea>')
			    .addClass('raw-textarea')
			    .text(word.example)
			    .attr('rows', 4)
			    .attr('id', 'textarea' + index)
			   );

		// source of the example
		$singleExampleDiv
		    .append($('<p>')
			    .addClass('source')
			    .text('źródło: ' + word.source)
			   );

		// meaning selector: if words have multiple meanings, one of them must be selected
		$selectdiv = $('<div>')
		    .addClass('def-selector')
		    .text('wybierz znaczenie: ')
		    .appendTo($singleExampleDiv);

		$select = $('<select>')
		    .addClass('num_selector')
		    .appendTo($selectdiv);

		// if there's only one meaning, show the selector but don't require the user to select a value
		if (word.definitions.length > 1) {
		    $select.append($('<option>', {value: ''}));
		}

		$.each(word.definitions, function(def_index, def_value){
		    $select.append($('<option>', {value: def_value.num, text: def_value.num}));
		    $defdiv.append(wikifyExample($defdiv, '(' + def_value.num + ') ' + def_value.text));
		});


		// good/bad example buttons
		$okbutton = $('<div>')
		    .addClass('toggle-button')
		    .addClass('good-button')
		    .attr('data-index', index)
		    .text('dobry przykład')
		    .appendTo($singleExampleDiv);

		$badbutton = $('<div>')
		    .addClass('toggle-button')
		    .addClass('bad-button')
		    .attr('data-index', index)
		    .text('zły przykład')
		    .appendTo($singleExampleDiv);
		
		// if the page has already been edited, select respective buttons
		if (word.good_example === true) {
		    $okbutton.addClass('toggle-button-selected-good');
		}
		if (word.bad_example === true) {
		    $badbutton.addClass('toggle-button-selected-bad');
		}
		
		
		$okbutton.click(verifyButtonAction(content, 'good'));
		$badbutton.click(verifyButtonAction(content, 'bad'));
		
	    });
	    

	    var prevNextButtonAction = function(prev_or_next) {
		return function(event) {
		    event.preventDefault();
		    if (!$('.current').hasClass(prev_or_next === 'prev' ? 'first' : 'last')) {
			
			if (prev_or_next === 'prev') {
			    $('.current').hide().removeClass('current')
				.prev().show().addClass('current');
			}
			else if (prev_or_next === 'next') {
			    $('.current').hide().removeClass('current')
				.next().show().addClass('current');
			}
			
			if ($('.current').hasClass(prev_or_next === 'prev' ? 'first' : 'last')) {
			    $('#' + prev_or_next).attr('disabled', true);
			}
			$('#' + (prev_or_next === 'prev' ? 'next' : 'prev')).attr('disabled', null);
		    };
		};
	    };

	    // prev/next buttons taken from http://jsfiddle.net/Qw75j/7/
	    $prevButton = $('<button>')
		.attr('id', 'prev')
		.attr('disabled', 'disabled')
		.text('Poprzedni')
		.click(prevNextButtonAction('prev'))
		.appendTo($editbox);

	    
	    $nextButton = $('<button>')
		.attr('id', 'next')
		.text('Następny')
		.click(prevNextButtonAction('next'))
		.appendTo($editbox);


        }

	// add keyboard shortcuts for "next", "previous", "good example" and "bad example"
	// $(document).on('keyup', null, 'ctrl+left', prevNextButtonAction('prev'));
	// $(document).on('keyup', null, 'ctrl+right', prevNextButtonAction('next'));
	// $(document).on('keyup', null, 'ctrl+up', verifyButtonAction('good'));
	// $(document).on('keyup', null, 'ctrl+down', verifyButtonAction('bad'));


	mw.util.addCSS( css.join( ' ' ) );
    } );
} );

function wikifyExample($div, exampleText) {
    $.getJSON(
	mw.util.wikiScript( 'api' ),
	
	{'format': 'json',
	 'action': 'parse',
	 'text': String(exampleText),
	 'prop': 'text',
	 'disablelimitreport': ''
	}
	
    )
	.done(function(data){
	    $div.append($(data.parse.text['*']));
	});
}