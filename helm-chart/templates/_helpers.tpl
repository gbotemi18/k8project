{{/*
Expand the name of the chart.
*/}}
{{- define "ip-reversal-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ip-reversal-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ip-reversal-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ip-reversal-app.labels" -}}
helm.sh/chart: {{ include "ip-reversal-app.chart" . }}
{{ include "ip-reversal-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ip-reversal-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ip-reversal-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ip-reversal-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ip-reversal-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "ip-reversal-app.secretName" -}}
{{- if .Values.secrets.enabled }}
{{- printf "%s-secrets" (include "ip-reversal-app.fullname" .) }}
{{- else }}
{{- printf "%s-secrets" (include "ip-reversal-app.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Create the database URL
*/}}
{{- define "ip-reversal-app.databaseUrl" -}}
{{- if .Values.database.external.enabled }}
{{- printf "postgresql://%s:%s@%s:%d/%s" .Values.database.external.user .Values.database.external.password .Values.database.external.host .Values.database.external.port .Values.database.external.name }}
{{- else }}
{{- printf "postgresql://%s:%s@%s:%d/%s" .Values.database.internal.user .Values.database.internal.password (include "ip-reversal-app.fullname" .) .Values.database.internal.port .Values.database.internal.name }}
{{- end }}
{{- end }} 