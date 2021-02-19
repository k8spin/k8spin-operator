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
                        <div class=\"column\" id=\""+ org.id + "-resources\">\
                        </div>\
                        <div class=\"column\" id=\""+ org.id + "-cpu-history\">\
                        </div>\
                        <div class=\"column\" id=\""+ org.id + "-memory-history\">\
                        </div>\
                    </div>\
                </div>";
            $("#orgs").append(new_box);
            organization_resources(org);
            organization_history(org);
        }
    });
}

function organization_resources(org) {
    api_org_resources = "/api/organizations/" + org.id + "/resources";
    $.getJSON(api_org_resources, function (data) {
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
        $("#" + org.id + "-resources").append(content);
    });
}

function organization_history(org) {
    api_org_resources = "/api/organizations/" + org.id + "/history";
    $.getJSON(api_org_resources, function (data) {
        // Prepare the canvas
        cpuContent = "<canvas id=\"" + org.id + "-cpu-chart\"></canvas>";
        memoryContent = "<canvas id=\"" + org.id + "-memory-chart\"></canvas>";
        $("#" + org.id + "-cpu-history").append(cpuContent);
        $("#" + org.id + "-memory-history").append(memoryContent);
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
        for (var i = (data.length-1); i >= 0; i--) {
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
        draw_graph(chartCPUData, chartOptions, org.id + "-cpu-chart");
        draw_graph(chartMemoryData, chartOptions, org.id + "-memory-chart");
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
