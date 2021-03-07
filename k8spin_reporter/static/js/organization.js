$(document).ready(function () {
    refresh();
    $("#refresh").click(function () {
        refresh();
    });
});

function refresh() {
    organization_id = $("#organization_id").val();
    if (organization_id === "") {
        organizations();
    } else {
        organization(organization_id);
    }
}


function organization(organization_id) {
    endpoint = "/api/organizations/" + organization_id
    $.getJSON(endpoint, function (data) {
        $("#orgs").empty();
        org = data;
        tenants_page_url = "/organizations/" + organization_id + "/tenants"
        var new_box = "\
            <div class=\"box\">\
                <div class=\"columns\"> \
                    <div class=\"column is-one-fifth\">\
                        "+ org.name + "\
                    </br>Tenants: <a href=\""+ tenants_page_url + "\"<i class=\"fas fa-info\"></i></a></div>\
                    <div class=\"column\" id=\""+ org.id + "-resources\">\
                    </div>\
                    <div class=\"column\" id=\""+ org.id + "-cpu-history\">\
                    </div>\
                    <div class=\"column\" id=\""+ org.id + "-memory-history\">\
                    </div>\
                </div>\
                <div class=\"columns\"> \
                    <div class=\"column\" id=\""+ org.id + "-tenants\">\
                    </div>\
                </div>\
            </div>";
        $("#orgs").append(new_box);
        organization_resources(org);
        organization_tenants(org);
        organization_history(org);
    });
}

function organizations() {
    $.getJSON('/api/organizations', function (data) {
        $("#orgs").empty();
        for (var i = 0; i < data.length; i++) {
            org = data[i];
            organization_page_url = "/organizations/" + org.id
            var new_box = "\
                <div class=\"box\">\
                    <div class=\"columns\"> \
                        <div class=\"column is-one-fifth\">\
                            "+ org.name + "</br>\
                        </br>Info: <a href=\""+ organization_page_url + "\"<i class=\"fas fa-info\"></i></a></div>\
                        <div class=\"column\" id=\""+ org.id + "-resources\">\
                        </div>\
                        <div class=\"column\" id=\""+ org.id + "-cpu-history\">\
                        </div>\
                        <div class=\"column\" id=\""+ org.id + "-memory-history\">\
                        </div>\
                    </div>\
                    <div class=\"columns\"> \
                        <div class=\"column\" id=\""+ org.id + "-tenants\">\
                        </div>\
                    </div>\
                </div>";
            $("#orgs").append(new_box);
            organization_resources(org);
            organization_history(org);
        }
    });
}

function organization_tenants(org) {
    api_org_tenants = "/api/organizations/" + org.id + "/tenants";

    $.getJSON(api_org_tenants, function (data) {
        tbody = ""
        for (var i = 0; i < data.length; i++) {
            tenant = data[i]
            tenant_page_url = "/organizations/" + org.id + "/tenants/" + tenant.id
            tbody = tbody + "\
            <tr>\
                <td>"+ tenant.name + "</td>\
                <td id=\""+ tenant.id + "-memory\"></td>\
                <td id=\""+ tenant.id + "-cpu\"></td>\
                <td><a href=\""+ tenant_page_url + "\"<i class=\"fas fa-info\"></i></a></td>\
            </tr>\
            ";
            tenant_resources(org, tenant);
        }

        content = "\
        <table class=\"table\">\
            <thead>\
                <tr>\
                    <th>Name</th>\
                    <th>Memory</th>\
                    <th>CPU</th>\
                    <th>Details</th>\
                </tr>\
            </thead>\
            <tbody id=\""+ org.id + "-tenants-table\">\
            "+ tbody + "\
            </tbody>\
        </table>";
        $("#" + org.id + "-tenants").append(content);
    });
}

function tenant_resources(org, tenant) {
    api_tenant_resources = "/api/organizations/" + org.id + "/tenants/" + tenant.id + "/resources";
    $.getJSON(api_tenant_resources, function (data) {
        cpu = data.used_cpu + "/" + data.allocated_cpu
        memory = data.used_memory + "/" + data.allocated_memory
        $("#" + tenant.id + "-cpu").append(cpu);
        $("#" + tenant.id + "-memory").append(memory);
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
