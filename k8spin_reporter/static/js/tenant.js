$(document).ready(function () {
    refresh();
    $("#refresh").click(function () {
        refresh();
    });
});

function refresh() {
    organization_id = $("#organization_id").val();
    tenant_id = $("#tenant_id").val();
    if (tenant_id === "") {
        tenants(organization_id);
    } else {
        one_tenant(organization_id, tenant_id);
    }
}

function tenants(organization_id) {
    endpoint = "/api/organizations/" + organization_id + "/tenants"
    $.getJSON(endpoint, function (data) {
        $("#tenant").empty();
        for (var i = 0; i < data.length; i++) {
            tenant = data[i];
            tenant_page_url = "/organizations/" + organization_id + "/tenants/" + tenant.id
            var new_box = "\
                <div class=\"box\">\
                    <div class=\"columns\"> \
                        <div class=\"column is-one-fifth\">\
                            "+ tenant.name + "\
                        </br>Info: <a href=\""+ tenant_page_url + "\"<i class=\"fas fa-info\"></i></a></div>\
                        <div class=\"column\" id=\""+ tenant.id + "-resources\">\
                        </div>\
                        <div class=\"column\" id=\""+ tenant.id + "-cpu-history\">\
                        </div>\
                        <div class=\"column\" id=\""+ tenant.id + "-memory-history\">\
                        </div>\
                    </div>\
                    <div class=\"columns\"> \
                        <div class=\"column\" id=\""+ tenant.id + "-spaces\">\
                        </div>\
                    </div>\
                </div>";
            $("#tenant").append(new_box);
            tenant_resources(organization_id, tenant);
            tenant_history(organization_id, tenant);
        }
    });
}

function one_tenant(organization_id, tenant_id) {
    endpoint = "/api/organizations/" + organization_id + "/tenants/" + tenant_id
    $.getJSON(endpoint, function (data) {
        $("#tenant").empty();
        tenant = data;
        spaces_page_url = "/organizations/" + organization_id + "/tenants/" + tenant.id + "/spaces"
        var new_box = "\
            <div class=\"box\">\
                <div class=\"columns\"> \
                    <div class=\"column is-one-fifth\">\
                        "+ tenant.name + "\
                    </br>Spaces: <a href=\""+ spaces_page_url + "\"<i class=\"fas fa-info\"></i></a></div>\
                    <div class=\"column\" id=\""+ tenant.id + "-resources\">\
                    </div>\
                    <div class=\"column\" id=\""+ tenant.id + "-cpu-history\">\
                    </div>\
                    <div class=\"column\" id=\""+ tenant.id + "-memory-history\">\
                    </div>\
                </div>\
                <div class=\"columns\"> \
                    <div class=\"column\" id=\""+ tenant.id + "-spaces\">\
                    </div>\
                </div>\
            </div>";
        $("#tenant").append(new_box);
        tenant_resources(organization_id, tenant);
        tenant_history(organization_id, tenant);
        tenant_spaces(organization_id, tenant);
    });
}

function tenant_resources(organization_id, tenant) {
    api_tenant_resources = "/api/organizations/" + organization_id + "/tenants/" + tenant.id + "/resources";
    $.getJSON(api_tenant_resources, function (data) {
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
        $("#" + tenant.id + "-resources").append(content);
    });
}

function tenant_spaces(organization_id, tenant) {
    api_tenant_spaces = "/api/organizations/" + organization_id + "/tenants/" + tenant.id + "/spaces";
    $.getJSON(api_tenant_spaces, function (data) {
        tbody = ""
        for (var i = 0; i < data.length; i++) {
            space = data[i]
            space_page_url = "/organizations/" + organization_id + "/tenants/" + tenant.id + "/spaces/" + space.id
            tbody = tbody + "\
            <tr>\
                <td>"+ space.name + "</td>\
                <td id=\""+ space.id + "-memory\"></td>\
                <td id=\""+ space.id + "-cpu\"></td>\
                <td><a href=\""+ space_page_url + "\"<i class=\"fas fa-info\"></i></a></td>\
            </tr>\
            ";
            space_resources(organization_id, tenant, space);
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
            <tbody id=\""+ tenant.id + "-spaces-table\">\
            "+ tbody + "\
            </tbody>\
        </table>";
        $("#" + tenant.id + "-spaces").append(content);
    });
}

function space_resources(organization_id, tenant, space) {
    api_space_resources = "/api/organizations/" + organization_id + "/tenants/" + tenant.id + "/spaces/" + space.id + "/resources";
    $.getJSON(api_space_resources, function (data) {
        cpu = data.used_cpu + "/" + data.allocated_cpu
        memory = data.used_memory + "/" + data.allocated_memory
        $("#" + space.id + "-cpu").append(cpu);
        $("#" + space.id + "-memory").append(memory);
    });
}

function tenant_history(organization_id, tenant) {
    api_tenant_resources = "/api/organizations/" + organization_id + "/tenants/" + tenant.id + "/history";
    $.getJSON(api_tenant_resources, function (data) {
        // Prepare the canvas
        cpuContent = "<canvas id=\"" + tenant.id + "-cpu-chart\"></canvas>";
        memoryContent = "<canvas id=\"" + tenant.id + "-memory-chart\"></canvas>";
        $("#" + tenant.id + "-cpu-history").append(cpuContent);
        $("#" + tenant.id + "-memory-history").append(memoryContent);
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
        draw_graph(chartCPUData, chartOptions, tenant.id + "-cpu-chart");
        draw_graph(chartMemoryData, chartOptions, tenant.id + "-memory-chart");
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
