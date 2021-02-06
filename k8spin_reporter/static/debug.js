$(document).ready(function () {
    refresh();
    $("#refresh").click(function () {
        refresh();
    });
});

function refresh() {
    organizations();
}

function organizations() {
    $.getJSON('/api/organizations', function (data) {
        $("#orgs").empty();
        for (var i = 0; i < data.length; i++) {
            org = data[i];
            var new_box = "\
                <div class=\"box\">\
                    <div class=\"columns\"> \
                        <div class=\"column is-one-fifth\">\
                            "+ org.name + "\
                        </div>\
                        <div class=\"column\" id=\""+ org.id + "\">\
                        </div>\
                    </div>\
                </div>";
            $("#orgs").append(new_box);
            organization_resources(org);
        }
    });
}

function organization_resources(org) {
    api_org_resources = "/api/organizations/" + org.id + "/resources";
    console.log(api_org_resources);
    $.getJSON(api_org_resources, function (data) {
        content = "\
        <p>\
        <span class=\"icon-text\"> \
            <span class=\"icon\"> \
                <i class=\"fas fa-memory\"></i> \
            </span> \
        <span>"+data.memory+"</span> \
        </span></p> \
        <p>\
        <span class=\"icon-text\"> \
            <span class=\"icon\"> \
                <i class=\"fas fa-microchip\"></i> \
            </span> \
        <span>"+data.cpu+"</span> \
        </span></p>"
        $("#" + org.id + "").append(content);
    });
}
