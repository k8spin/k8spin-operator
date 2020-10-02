{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "k8spin-operator.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "k8spin-operator.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "k8spin-operator.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create the name of the k8spin_operator service account to use
*/}}
{{- define "k8spin_operator.serviceAccountName" -}}
{{- if .Values.k8spin_operator.serviceAccount.create -}}
    {{ default (include "k8spin-operator.fullname" .) .Values.k8spin_operator.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.k8spin_operator.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Create the name of the k8spin_webhook service account to use
*/}}
{{- define "k8spin_webhook.serviceAccountName" -}}
{{- if .Values.k8spin_webhook.serviceAccount.create -}}
    {{- $name := printf "%s-%s" (include "k8spin-operator.fullname" .) "webhook" -}}
    {{ default $name .Values.k8spin_webhook.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.k8spin_webhook.serviceAccount.name }}
{{- end -}}
{{- end -}}
