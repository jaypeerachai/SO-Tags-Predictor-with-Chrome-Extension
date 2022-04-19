var tags = tags.split(',');
var tags_fill = "";
for (var i = 0; i < tags.length; i++) {
    var tag = tags[i];
    tags_fill += tag + " ";
}

// inject the tag(s)
fill_tag(tags_fill);

// function to fill the tag(s)
function fill_tag(data){
    fillField(document.querySelector('input[id="tageditor-replacing-tagnames--input"]'), data);
}

function fillField(selector, value)
{
    var field = selector();
    fillField(field, value);
}

function fillField(field, value){
    if(field){
        field.value = value;
    }  
}
