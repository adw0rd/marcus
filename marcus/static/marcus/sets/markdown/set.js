// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// MarkDown tags example
// http://en.wikipedia.org/wiki/Markdown
// http://daringfireball.net/projects/markdown/
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------

var fullScreen = {
    'on': function(markItUp) {
        var textarea = $(markItUp.textarea);
        markItUpTextareaOGHeight = textarea.innerHeight();
        textarea.parent().parent().addClass('markItUp-fullScreen');
        textarea.css('height', "100%"); // ($('.markItUp-fullScreen').innerHeight() - 90) + "px"
        textarea.css('width', "100%");
    },
    'off': function() {
        $('.markItUp').removeClass('markItUp-fullScreen');
        $('textarea').css('height', markItUpTextareaOGHeight + "px");
    }
}

mySettings = {
    previewParserPath:    '/markitup/preview/',
    onShiftEnter:        {keepDefault:false, openWith:'\n\n'},
    markupSet: [
        {name:'First Level Heading', key:'1', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
        {name:'Second Level Heading', key:'2', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
        {name:'Heading 3', key:'3', openWith:'### ', placeHolder:'Your title here...' },
        {name:'Heading 4', key:'4', openWith:'#### ', placeHolder:'Your title here...' },
        {name:'Heading 5', key:'5', openWith:'##### ', placeHolder:'Your title here...' },
        {name:'Heading 6', key:'6', openWith:'###### ', placeHolder:'Your title here...' },
        {separator:'---------------' },        
        {name:'Bold', key:'B', openWith:'**', closeWith:'**'},
        {name:'Italic', key:'I', openWith:'_', closeWith:'_'},
        {separator:'---------------' },
        {name:'Bulleted List', openWith:'- ' },
        {name:'Numeric List', openWith:function(markItUp) {
            return markItUp.line+'. ';
        }},
        {separator:'---------------' },
        {name:'Picture', key:'P', replaceWith:'![[![Alternative text]!]]([![Url:!:http://]!] "[![Title]!]")'},
        {name:'Link', key:'L', openWith:'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder:'Your text to link here...' },
        {separator:'---------------'},    
        {name:'Quotes', openWith:'> '},
        {name:'Code Block / Code', openWith:'(!(\t|!|`)!)', closeWith:'(!(`)!)'},
        {separator:'---------------'},
        {name:'Preview', call:'preview', className:"preview"},
        {name:'Full Screen', className:'fullScreen', openWith:function(markItUp) {
            if ($('.markItUp').hasClass('markItUp-fullScreen')) {
                fullScreen['off']();
            } else {
                fullScreen['on'](markItUp);
            }
        }}
    ]
}

$(document).keypress(function(button) {
    if (button.keyCode && button.keyCode == 27) {
        // ESC
        fullScreen['off']();
    }
});

// mIu nameSpace to avoid conflict.
miu = {
    markdownTitle: function(markItUp, char) {
        heading = '';
        n = $.trim(markItUp.selection||markItUp.placeHolder).length;
        // work around bug in python-markdown where header underlines must be at least 3 chars
        if (n < 3) { n = 3; }
        for(i = 0; i < n; i++) {
            heading += char;
        }
        return '\n'+heading;
    }
}
