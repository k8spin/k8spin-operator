$(document).ready(function () {
    refresh();
    $("#refresh").click(function () {
        refresh();
    });
});

function refresh() {
    organization_id = $("#organization_id").val();
    tenant_id = $("#tenant_id").val();
    space_id = $("#space_id").val();
    if (space_id === "") {
        spaces(organization_id, tenant_id);
    } else {
        one_space(organization_id, tenant_id, space_id);
    }
}

function spaces(organization_id, tenant_id) {
    endpoint = "/api/organizations/" + organization_id + "/tenants/" + tenant_id + "/spaces"
    $.getJSON(endpoint, function (data) {
        $("#space").empty();
        for (var i = 0; i < data.length; i++) {
            space = data[i];
            space_page_url = "/organizations/" + organization_id + "/tenants/" + tenant_id + "/spaces/" + space.id
            var new_box = "\
                <div class=\"box\">\
                    <div class=\"columns\"> \
                        <div class=\"column is-one-fifth\">\
                            "+ space.name + "\
                        </br>Info: <a href=\""+ space_page_url + "\"<i class=\"fas fa-info\"></i></a></div>\
                        <div class=\"column\" id=\""+ space.id + "-resources\">\
                        </div>\
                        <div class=\"column\" id=\""+ space.id + "-cpu-history\">\
                        </div>\
                        <div class=\"column\" id=\""+ space.id + "-memory-history\">\
                        </div>\
                    </div>\
                </div>";
            $("#space").append(new_box);
            space_resources(organization_id, tenant_id, space);
            space_history(organization_id, tenant_id, space);
        }
    });
}



function one_space(organization_id, tenant_id, space_id) {
    endpoint = "/api/organizations/" + organization_id + "/tenants/" + tenant_id + "/spaces/" + space_id
    $.getJSON(endpoint, function (data) {
        $("#space").empty();
        space = data;
        var new_box = "\
            <div class=\"box\">\
                <div class=\"columns\"> \
                    <div class=\"column is-one-fifth\">\
                        "+ space.name + "\
                    </div>\
                    <div class=\"column\" id=\""+ space.id + "-resources\">\
                    </div>\
                    <div class=\"column\" id=\""+ space.id + "-cpu-history\">\
                    </div>\
                    <div class=\"column\" id=\""+ space.id + "-memory-history\">\
                    </div>\
                </div>\
            </div>";
        $("#space").append(new_box);
        space_resources(organization_id, tenant_id, space);
        space_history(organization_id, tenant_id, space);
    });
}

function space_resources(organization_id, tenant_id, space) {
    api_space_resources = "/api/organizations/" + organization_id + "/tenants/" + tenant_id + "/spaces/" + space.id + "/resources";
    $.getJSON(api_space_resources, function (data) {
        content = "\
        <p>\
        <span class=\"icon-text\"> \
            <span class=\"icon\"> \
                <i class=\"fas fa-memory\"></i> \
            </span> \
        <span>"+ data.used_memory + "/" + data.allocated_memory + "</span> \
        </span></p> \
        <p>\
        <span class=\"icon-text\"> \
            <span class=\"icon\"> \
                <i class=\"fas fa-microchip\"></i> \
            </span> \
        <span>"+ data.used_cpu + "/" + data.allocated_cpu + "</span> \
        </span></p>"
        $("#" + space.id + "-resources").append(content);
    });
}

function space_history(organization_id, tenant_id, space) {
    api_space_resources = "/api/organizations/" + organization_id + "/tenants/" + tenant_id + "/spaces/" + space.id + "/history";
    $.getJSON(api_space_resources, function (data) {
        // Prepare the canvas
        cpuContent = "<canvas id=\"" + space.id + "-cpu-chart\"></canvas>";
        memoryContent = "<canvas id=\"" + space.id + "-memory-chart\"></canvas>";
        $("#" + space.id + "-cpu-history").append(cpuContent);
        $("#" + space.id + "-memory-history").append(memoryContent);
        // Prepare the data
        chartCPUData = {
            labels: [],
            datasets: []
        }
        chartMemoryData = {
            labels: [],
            datasets: []
        }
        cpu_used_records = {
            label: "CPU Used",
            data: []
        }
        memory_used_records = {
            label: "Memory Used",
            data: []
        }
        cpu_allocated_records = {
            label: "CPU Allocated",
            data: []
        }
        memory_allocated_records = {
            label: "Memory Allocated",
            data: []
        }
        for (var i = (data.length - 1); i >= 0; i--) {
            record = data[i]

            chartCPUData.labels.push(record.day);
            chartMemoryData.labels.push(record.day);

            cpu_used_records.data.push(record.used_cpu);
            cpu_allocated_records.data.push(record.allocated_cpu);
            memory_used_records.data.push(record.used_memory);
            memory_allocated_records.data.push(record.allocated_memory);
        }
        chartCPUData.datasets.push(cpu_used_records);
        chartMemoryData.datasets.push(memory_used_records);
        chartCPUData.datasets.push(cpu_allocated_records);
        chartMemoryData.datasets.push(memory_allocated_records);
        // TODO Optimize
        var chartOptions = {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 80,
                    fontColor: 'black'
                }
            }
        };
        draw_graph(chartCPUData, chartOptions, space.id + "-cpu-chart");
        draw_graph(chartMemoryData, chartOptions, space.id + "-memory-chart");
    });
}

function draw_graph(data, options, chart_id) {
    var ctx = document.getElementById(chart_id).getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
}
