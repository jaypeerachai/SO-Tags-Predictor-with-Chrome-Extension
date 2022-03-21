var add_tag_button = document.getElementById("add_tags");
var submit_button = document.getElementById("submit");
var reset_button = document.getElementById("reset");

function send_input(input_json){
    // chrome.extension.getBackgroundPage().console.log(input_json);
    var xhr = new XMLHttpRequest();
    var url = "http://127.0.0.1:5000/";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        chrome.extension.getBackgroundPage().console.log(xhr.status);
        chrome.extension.getBackgroundPage().console.log(xhr);
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var tag_div = document.getElementById('tags_list');
            var loading_div = document.getElementById('loading');
            var sorry_div = document.getElementById("sorry");
            
            add_tag_button.style.display = 'none';
            tag_div.style.display = 'none';
            sorry_div.style.display = 'block';
            loading_div.style.display = 'block';
            var status = xhr.status;
            if (status === 0 || (status >= 200 && status < 400)) {
                display_results(xhr.responseText);
            } else {
                loading_div.style.display = 'none';
                sorry_div.style.display = 'block';
                sorry_div.innerHTML = "<p>Sorry, there was a problem with the request. Please try again later.</p>";
            }
        } else {
            loading_div.style.display = 'none';
            sorry_div.style.display = 'block';
            sorry_div.innerHTML = "<p>Sorry, there was a problem with the request. Please try again later.</p>";
        }
    };
    xhr.send(input_json);
}

function display_results(output_json) {
    var loading_div = document.getElementById("loading");
    var sorry_div = document.getElementById("sorry");

    sorry_div.style.display = 'none';
    loading_div.style.display = 'none';

    var tag_div = document.getElementById("tags_list");
    var response = output_json;
    var tag_json = JSON.parse(response);

    // if json response is empty
    if (tag_json && Object.keys(tag_json).length === 0 && Object.getPrototypeOf(tag_json) === Object.prototype) {
        var sorry_div = document.getElementById("sorry");
        tag_div.style.display = 'none';
        sorry_div.style.display = 'block';
        sorry_div.innerHTML = "<p>Sorry, no tags found !!!</p>";
    } else {
        var tag_option = document.getElementById("tag_option");
        tag_option.options.length = 0;
        tag_div.style.display = 'block';
        submit_button.style.display = 'none';
        add_tag_button.style.display = 'block';
        reset_button.style.display = 'block';
        // chrome.extension.getBackgroundPage().console.log(typeof tag_json);
        // chrome.extension.getBackgroundPage().console.log(tag_json);
        for (var tag in tag_json) {
            // chrome.extension.getBackgroundPage().console.log(tag);
            var opt = document.createElement('option');
            prob = tag_json[tag];
            concat_result = tag + ": " + prob;
            opt.value = concat_result;
            opt.innerHTML = concat_result;
            opt.id = "tag_options";
            opt.style.marginTop = "4px";
            opt.style.marginBottom = "-2px";
            opt.style.marginLeft = "4px";
            tag_option.appendChild(opt);
            opt.addEventListener('dblclick', function() {
                chrome.extension.getBackgroundPage().console.log('dblclick');
                var api_key = "8hvLA7uVPEIp6wwaqNOF5w((";
                var site = "stackoverflow";
                var tag_name = this.value.split(':')[0]
                var url = "https://api.stackexchange.com/2.3/tags/{" + tag_name + "}/wikis"
                var tag_wiki_xhr = new XMLHttpRequest();
                tag_wiki_xhr.open("GET", url+"?site="+site+"&key="+api_key, true);
                tag_wiki_xhr.onreadystatechange = function () {
                    if (tag_wiki_xhr.readyState == XMLHttpRequest.DONE) {
                        var status = tag_wiki_xhr.status;
                        if (status === 0 || (status >= 200 && status < 400)) {
                            var tag_wiki_json = JSON.parse(tag_wiki_xhr.responseText);
                            var excerpt = tag_wiki_json['items'][0]['excerpt'];
                            alert(tag_name + "\n▬▬▬▬▬▬▬▬▬▬▬ஜ۩۞۩ஜ▬▬▬▬▬▬▬▬▬▬▬\n\n" + excerpt);
                        }
                    }
                };
                tag_wiki_xhr.send();
            });
        }
    }
}

function get_select_values(select) {
    var result = [];
    var options = select && select.options;
    var opt;
  
    for (var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];
        if (opt.selected) {
            result.push(opt.value || opt.text);
        }
    }
    return result;
}

submit_button.addEventListener('click', function() {
    chrome.extension.getBackgroundPage().console.log('submit');
    var loading_div = document.getElementById('loading');
    loading_div.style.display = 'block';
    var ele = document.getElementsByName('model');
    for(i = 0; i < ele.length; i++) {
        if(ele[i].checked){
            model = ele[i].value;
        }
    }
    var input_json = {
        "title": document.getElementById('title').value,
        "description": document.getElementById('description').value,
        "k": document.getElementById('k').value,
        "threshold": document.getElementById('threshold').value,
        "model": model,
    }
    var input_json_string = JSON.stringify(input_json);
    send_input(input_json_string);
});

reset_button.addEventListener('click', function() {
    chrome.extension.getBackgroundPage().console.log('reset');
    var tag_div = document.getElementById('tags_list');
    tag_div.style.display = 'none';
    add_tag_button.style.display = 'none';
    reset_button.style.display = 'none';
    submit_button.style.display = 'block';

});

add_tag_button.addEventListener('click', function() {
    console.log('add_tags');
    var tag_option = document.getElementById("tag_option");
    var selected_tags = get_select_values(tag_option);
    chrome.extension.getBackgroundPage().console.log(selected_tags);
    var tag_list = [];
    for (var i = 0; i < selected_tags.length; i++) {
        var tag = selected_tags[i];
        var only_tag = tag.split(':')[0];
        tag_list.push(only_tag);
    }
    chrome.extension.getBackgroundPage().console.log(tag_list);
    chrome.tabs.executeScript({
        code: `var tags = "${tag_list}";`
    }, function() {
        chrome.tabs.executeScript({
            file: 'injector.js'
        });
    });
});