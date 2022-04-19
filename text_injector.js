var title = title;
var description = description;

fill_text(title, description);


function fill_text(data, description){
    fillField(document.querySelector('input[id="title"]'), data);
    fillField(document.querySelector('textarea[id="wmd-input"]'), description);
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
