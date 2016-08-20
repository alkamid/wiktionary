// http://blog.dobryslownik.pl/po-co-przyklady-uzycia-w-slowniku/

var api = new mw.Api();

// Make sure the utilities module is loaded (will only load if not already)
var config = mw.config.get( [
	'wgPageName',
	'wgAction',
	'wgUserName'
] );

var markUnwikified = function( text ) {
	//https://regex101.com/r/sW8qF6/7
	var re = /((?:\S*\[\[.+?]]\S*|^|\s+)+)([^\s\-—–0-9]+(?:-[^\s\-]+)?|$)/g;
	var marked = text.replace(re, '$1<mark>$2</mark>');
	return marked;
};

var replaceNewline = function ( text, escapeBrackets ) {
	if ( escapeBrackets === true) {
		return text.replace( /(?:\r\n|\r|\n)/g, '&lt;br /&gt;' );
	}
	else {
		return text.replace( /(?:\r\n|\r|\n)/g, '<br />' );
	}
};

var verifyButtonAction = function( content, good_or_bad ) {
	return function( event ) {
		var exampleIndex = $( this ).closest( '.example-box' ).attr( 'data-example-index' );
	
		var $thisbutton = $( this );
		var $thatbutton = $( '.current.example-div' )
			.find( '*[data-example-index=' + exampleIndex + ']' )
			.find( ':not(.toggle-button.' + good_or_bad + '-button)' ); 
		var $selectordiv = $( '.current.example-div' )
			.find( '*[data-example-index=' + exampleIndex + ']' )
			.find( '.def-selector' );
	
		var selectorValue = $selectordiv.find( '.num_selector' ).val();
		if ( good_or_bad === 'good' && selectorValue === '' ) {
			$selectordiv.addClass( 'selector-div-unknown-choice' );
			return -1;
		}
	
		$selectordiv.removeClass( 'selector-div-unknown-choice' );
		
		$thisbutton.toggleClass( 'toggle-button-selected-' + good_or_bad );
		$thatbutton.removeClass( 'toggle-button-selected-' + ( good_or_bad === 'good' ? 'bad' : 'good' ) );
		
		var index = $thisbutton.closest( '.example-div' ).attr( 'data-index' );
		
		if ( good_or_bad === 'good' ) {
			if ( content[index].examples[exampleIndex].good_example === true ) {
				content[index].examples[exampleIndex].verificator = 'None';
				content[index].examples[exampleIndex].correct_num = 'None';
			}
			else if ( content[index].examples[exampleIndex].bad_example === true ) {
				content[index].examples[exampleIndex].bad_example = false;
				content[index].examples[exampleIndex].correct_num = selectorValue;
			}
			else {
				content[index].examples[exampleIndex].correct_num = selectorValue;
			}
			content[index].examples[exampleIndex].good_example = !content[index].examples[exampleIndex].good_example;
		}
		else if ( good_or_bad === 'bad' ) {
			if ( content[index].examples[exampleIndex].bad_example === true ) {
				content[index].examples[exampleIndex].verificator = 'None';
				content[index].examples[exampleIndex].correct_num = 'None';
			}
			else if ( content[index].examples[exampleIndex].good_example === true ) {
				content[index].examples[exampleIndex].good_example = false;
				content[index].examples[exampleIndex].correct_num = 'None';
			}
			content[index].examples[exampleIndex].bad_example = !content[index].examples[exampleIndex].bad_example;
		}
	
		content[index].examples[exampleIndex].verificator = config.wgUserName === null ? '{' + '{subst:REVISIONUSER}}' : config.wgUserName;
		
		var $textarea = $( this ).closest( '.example-box' ).find( '.textarea' );
		$textarea.html( markUnwikified ( $textarea.text() ) );
		
		document.editform.wpTextbox1.value = JSON.stringify( content, null, 4 );
	};
};
	
	// mw.loader.load( '//rawgit.com/jeresig/jquery.hotkeys/master/jquery.hotkeys.js' );
	/*TODO: <thedj> alkamid: usually, check if the external library is defined if you want to use it, and be prepared for it not being defined and you having to 'reschedule' another attempt to do you 'setup' at a later time, is the strategy often followed in this case.*/

	// Wait for the page to be parsed
$( document ).ready( function () {
	if ( config.wgAction === 'view' && $( '.firstHeading' ).text().replace( ' ', '_') === config.wgPageName ) {
		$( '#mw-content-text' ).empty();
		wikifyExample( $( '#mw-content-text' ), '{{Dodawanie_przykładów_intro}}' );
	}

	if ( $.inArray( mw.config.get( 'wgAction' ), [ 'edit', 'submit' ] ) === -1 ) {
		return;
	}

	// hide textarea
	$( '#wpTextbox1' ).hide();

	// add explanatory screenshot at the top
	$( '.wikiEditor-ui-top' ).prepend( '<img id="explain" style="max-width:100%" src="https://upload.wikimedia.org/wiktionary/pl/e/e6/Dodawanie_przyk%C5%82ad%C3%B3w_-_pomoc.png" />' );
	
	// until I find a way to redirect special characters etc. to my custom fields
	$( '#wikiEditor-ui-toolbar' ).hide();

	// and a button to hide/show it (and a cookie to control hide/show)
	$helpbutton = $( '<button>' )
		.text( 'pokaż/schowaj pomoc' )
		.addClass( 'help-screenshot-button' )
		.click( function () {
			$( '#explain' ).toggle();
			
			if ( $.cookie( 'wiktionary-examples-verification-help' ) === null ) {
				$.cookie( 'wiktionary-examples-verification-help', 1, {
					expires: 30,
					path: '/'
				} );
			}
			else {
				$.removeCookie( 'wiktionary-examples-verification-help' );
			}
			return false;
		})
		.prependTo( $( '.wikiEditor-ui-top' ) );

	if ( $.cookie( 'wiktionary-examples-verification-help' ) !== null ) {
		$( '#explain' ).hide();
	}
		
	// Content written by AlkamidBot is in JSON format
	var content = $.parseJSON( document.editform.wpTextbox1.value );
	
	// This is the main edit div for usage examples
	var $editbox = $( '<div>' )
		.attr( 'id', 'wikiEditor-ui-examples' )
		.prependTo( $( '.wikiEditor-ui-bottom' ) );
		
	$.each( content, function ( index, word ) {
	
		// for each word, a div is created - only one is set as "current" at a time,
		// and the other ones are hidden
		$singleExampleDiv = $( '<div>' )
			.addClass( 'example-div' )
			.attr( 'data-index', index)
			.appendTo( $editbox );
		

		// title in bold
		$singleExampleDiv
			.append( $( '<p>' )
				.append( $( '<b>' ).text( word.title ) )
			);
		
		// at the beginning, show only the first word
		if ( index === 0 ) {
			$singleExampleDiv.addClass( 'first current' );
		}

		// this class is important for deactivating the "next" button
		if ( index === content.length -1 ) {
			$singleExampleDiv.addClass( 'last' );
		}
		
		// container for definitions
		$defdiv = $( '<div>' )
			.addClass( 'defs-div' )
			.appendTo( $singleExampleDiv );
		
		// count meanings (used for dropdown menu later)
		var nums = [];
		var reNums = /\: \(([0-9]\.[0-9]{1,2})\)\s*/g;
		match = reNums.exec( word.definitions );
		while ( match !== null ) {
			nums.push( match[1] );
			match = reNums.exec( word.definitions );
		}
		
		$.each( word.examples, function ( ix, example ){
			
			// containter for example text
			$textdiv = $( '<div>' )
				.addClass( 'example-box' )
				.attr( 'data-example-index', ix )
				.appendTo( $singleExampleDiv );

			// buttons and selector container
			$buttonsdiv = $( '<div>' )
				.addClass( 'example-buttons' )
				.appendTo( $textdiv );

			// meaning selector: if words have multiple meanings, one of them must be selected
			$selectdiv = $( '<div>' )
				.addClass( 'def-selector' )
				.appendTo( $buttonsdiv );

			$select = $( '<select>' )
				.addClass( 'num_selector' )
				.appendTo( $selectdiv );

			// add options to select dropdown menu
			$.each( nums, function ( ix, val ) {
				$option = $( '<option>', { value: val, text: val } )
					.appendTo( $select );
				if ( example.correct_num !== '' && val === example.correct_num ) {
					$option.attr( 'selected', 'selected' );
				}
			});
			
			$select.change( function() {
				content[index].examples[ix].correct_num = $( this ).children( ":selected" ).val();
				document.editform.wpTextbox1.value = JSON.stringify( content, null, 4 );
	    	});

			// if there's only one meaning, show the selector but don't require the user to select a value
			if ( $select.find( 'option' ).length > 1 ) {
				$select.prepend( $( '<option>', { value: '' } ) );
			}

			// good/bad example buttons
			$okbutton = $( '<div>' )
				.addClass( 'toggle-button' )
				.addClass( 'good-button' )
				.text( '✓' )
				.appendTo( $buttonsdiv );

			$buttonsdiv.append( $( '<br/>' ) );

			$badbutton = $( '<div>' )
				.addClass( 'toggle-button' )
				.addClass( 'bad-button' )
				.text( '✗' )
				.appendTo( $buttonsdiv );

			// if the page has already been edited, select respective buttons
			if ( example.good_example === true ) {
				$okbutton.addClass( 'toggle-button-selected-good' );
			}
			if ( example.bad_example === true ) {
				$badbutton.addClass( 'toggle-button-selected-bad' );
			}
		
			// container for raw text ([[such]] [[as]] [[this]])
			$rawTextdiv = $( '<div>' )
				.addClass( 'raw-text' )
				.appendTo( $textdiv );

			// left context - in case the usage is not clear from what's been copied into the textbox
			$leftcontext = $( '<p>' )
				.addClass( 'left-context' )
				.text( example.left_extra )
				.appendTo( $rawTextdiv );

			$wikifiedDiv= $( '<div>' )
				.addClass( 'wikified-text-box' )
				.appendTo( $textdiv );

			// refresh button - I put it in another diff for it to stay in one place
			$reloadButton = $( '<button>' )
				.addClass( 'refresh-button' )
				.text( 'odśwież' )
				.appendTo( $wikifiedDiv );

			$reloadButton.click( function () {
				$div_to_refresh = $( this ).closest( '.example-box' ).find( '.wikified-text' );
				text_to_refresh_from = $( this ).closest( '.example-box' ).find( '.textarea' ).text();
				$div_to_refresh.empty();
				wikifyExample( $div_to_refresh, text_to_refresh_from, word.title );
				return false;
			});

			// wikified text - can be refreshed
			$wikifiedTextdiv = $( '<div>' )
				.addClass( 'wikified-text' )
				.attr( 'data-example-index', ix )
				.appendTo( $wikifiedDiv );

			wikifyExample( $wikifiedTextdiv, replaceNewline( example.example, false ), word.title );

			// editable wikitext
			$textarea = $( '<div>' )
				.addClass( 'textarea' )
				.prop('contenteditable', true)
				.html( replaceNewline( markUnwikified( example.example), true ) )
				.on( 'keyup', function() {
					content[index].examples[ix].example = $( this ).text();
					document.editform.wpTextbox1.value = JSON.stringify( content, null, 4 );
				})
				.on( 'paste', function (e) {
					//http://stackoverflow.com/a/19269040/2261298 - plain text pasting
					e.preventDefault();
					var text = (e.originalEvent || e).clipboardData.getData('text/plain') || prompt('Wklej tekst.');
					document.execCommand('inserttext', false, text);
				})
				.appendTo($rawTextdiv);
			
			// source of the example
			var $sourcePara = $( '<p>' )
				.addClass( 'source' )
				.appendTo( $wikifiedDiv );
				
			
			$sourcePara.append( example.source.authors );
			
			if ( example.source.authors != '' ) {
				$sourcePara.append( ', ' );
			}
			
			if ( 'article_title' in example.source && 'journal_title' in example.source) {
				//for new API results (08/2016)
				$sourcePara.append( '<em>' + example.source.article_title + '</em>' );
				$sourcePara.append( ', „' + example.source.journal_title + '”' );
			}	
			else if ( 'article_title' in example.source) {
				//for old API results (to be deleted when all pages have been refreshed)
				$sourcePara.append( '<em>' + example.source.article_title + '</em>' );
				$sourcePara.append( ', „' + example.source.pub_title + '”' );
			}
			else if ( 'pub_title' in example.source) {
				$sourcePara.append( '<em>' + example.source.pub_title + '</em>' );
			}
			
			$sourcePara.append( ', ' + example.source.date + '.' );

			if ( 'hash' in example.source && 'match_start' in example.source && 'match_end' in example.source ) {
				var nkjpLink = 'http://nkjp.uni.lodz.pl/ParagraphMetadata?pid=' + example.source.hash +
					'&match_start=' + example.source.match_start +
					'&match_end=' + example.source.match_end +
					'&wynik=1';
				$sourcePara.append( ' <a href="' + nkjpLink + '">(NKJP)</a>');
			}
			else if ('id' in example.source) {
				var nkjpLink = 'http://pelcra.clarin-pl.eu/NKJP/#page/open/context/NKJP/' + example.source.id + '/1'
				$sourcePara.append( ' <a href="' + nkjpLink + '">(NKJP)</a>');
			}
			
			
			$okbutton.click( verifyButtonAction( content, 'good' ) );
			$badbutton.click( verifyButtonAction( content, 'bad' ) );


			if ( ix === 0 ) {
				$singleExampleDiv.append( $( '<hr/>' ) );
			}
		});

		wikifyExample( $defdiv, word.definitions );

	});

	var prevNextButtonAction = function ( content, prev_or_next ) {
		return function( event ) {
			event.preventDefault();

			var index = $( '.current.example-div' ).attr( 'data-index' );

			document.editform.wpTextbox1.value = JSON.stringify( content, null, 4 );
			if ( !$( '.current' ).hasClass( prev_or_next === 'prev' ? 'first' : 'last' ) ) {
				
				if ( prev_or_next === 'prev' ) {
					$( '.current' )
						.hide()
						.removeClass( 'current' )
						.prev()
						.show()
						.addClass( 'current' );
				}
				else if ( prev_or_next === 'next' ) {
					$( '.current' )
						.hide()
						.removeClass( 'current' )
						.next()
						.show()
						.addClass( 'current' );
				}
				
				if ( $( '.current' ).hasClass( prev_or_next === 'prev' ? 'first' : 'last' ) ) {
					$( '#' + prev_or_next ).attr( 'disabled', true );
				}
				$( '#' + ( prev_or_next === 'prev' ? 'next' : 'prev' ) ).attr( 'disabled', null );
			};
		};
	};

	// prev/next buttons taken from http://jsfiddle.net/Qw75j/7/
	$prevButton = $( '<button>' )
		.attr( 'id', 'prev' )
		.attr( 'disabled', 'disabled' )
		.text( 'Poprzedni')
		.click( prevNextButtonAction( content, 'prev' ) )
		.appendTo( $editbox );
	
	$nextButton = $( '<button>' )
		.attr( 'id', 'next' )
		.text( 'Następny' )
		.click( prevNextButtonAction( content, 'next' ) )
		.appendTo( $editbox );

	if ( $( '.current' ).hasClass( 'last' ) ) {
		$nextButton.attr( 'disabled', 'disabled' );
	};

	// add keyboard shortcuts for "next", "previous", "good example" and "bad example"
	// $(document).on('keyup', null, 'ctrl+left', prevNextButtonAction('prev'));
	// $(document).on('keyup', null, 'ctrl+right', prevNextButtonAction('next'));
	// $(document).on('keyup', null, 'ctrl+up', verifyButtonAction('good'));
	// $(document).on('keyup', null, 'ctrl+down', verifyButtonAction('bad'));

} );

function wikifyExample( $div, exampleText, word ) {
	word = typeof word !== 'undefined' ? word : 'kdslamsd';
	api.parse( exampleText, {
		title: word,
		prop: 'text',
		disablelimitreport: true
	} ).done( function ( parsedText ) {
		$( parsedText ).appendTo( $div );
	} );
}
