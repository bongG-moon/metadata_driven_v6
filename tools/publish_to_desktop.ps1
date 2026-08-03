param(
    [string]$Target = "$env:USERPROFILE\Desktop\metadata_driven_v6"
)

$ErrorActionPreference = "Stop"
$Source = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$TargetFull = [IO.Path]::GetFullPath($Target)
$AuthoringEvidenceRelativePath = "validation_outputs\langflow_http_authoring_final_pass.json"
$AuthoringEvidenceName = [IO.Path]::GetFileName($AuthoringEvidenceRelativePath)
$OrderSalesEvidenceRelativePath = "validation_outputs\langflow_http_order_sales_final_pass.json"
$OrderSalesEvidenceName = [IO.Path]::GetFileName($OrderSalesEvidenceRelativePath)
$MigrationEvidenceRelativePath = "validation_outputs\langflow_http_migration_final_pass.json"
$MigrationEvidenceName = [IO.Path]::GetFileName($MigrationEvidenceRelativePath)
$PublishedValidationEvidence = @(
    "validation_outputs\api_terminal_fail_closed_final.json",
    "validation_outputs\domain_extension_safety_final.json",
    "validation_outputs\flow_source_sync_v6_final.json",
    "validation_outputs\generic_v2_support_pipeline_final.json",
    "validation_outputs\langflow_equivalent_pipeline_http_ready_final.json",
    "validation_outputs\langflow_http_authoring_final_pass.json",
    "validation_outputs\langflow_http_migration_final_pass.json",
    "validation_outputs\langflow_http_order_sales_final_pass.json",
    "validation_outputs\langflow_runtime_v6_final.json",
    "validation_outputs\live_blueprint_authoring_final.json",
    "validation_outputs\live_intent_models_candidate_cards_final.json",
    "validation_outputs\order_sales_component_cases_v6_final.json",
    "validation_outputs\prompt_extension_runtime_final.json",
    "validation_outputs\pytest_v6_final_latest.xml",
    "validation_outputs\runtime_cases_final.json",
    "validation_outputs\runtime_repeat_stability.json"
)

if ([IO.Path]::GetFileName($TargetFull) -ne "metadata_driven_v6") {
    throw "Refusing unexpected target folder: $TargetFull"
}

$DataAnalysisFlowName = "metadata_v6_data_analysis_flow_v6_standalone.json"
$AuthoringFlowNames = @(
    "metadata_v6_domain_authoring_flow_v6_standalone.json",
    "metadata_v6_dataset_catalog_authoring_flow_v6_standalone.json",
    "metadata_v6_main_filter_authoring_flow_v6_standalone.json"
)
$flowDirectory = Join-Path $Source "flow_exports"
$currentFlowFiles = @(Get-ChildItem -LiteralPath $flowDirectory -File -Filter "*_standalone.json")
if ($currentFlowFiles.Count -ne 4) {
    throw "Expected 4 current standalone Flow exports, found $($currentFlowFiles.Count)"
}
$currentFlowHashes = @{}
foreach ($flowFile in $currentFlowFiles) {
    $currentFlowHashes[$flowFile.Name] = (Get-FileHash -LiteralPath $flowFile.FullName -Algorithm SHA256).Hash
}

function Assert-ImportEvidenceCurrent {
    param(
        [object]$Imports,
        [string[]]$ExpectedFileNames,
        [string]$Label
    )
    $rows = @($Imports)
    if ($rows.Count -ne $ExpectedFileNames.Count) {
        throw "$Label evidence import count mismatch"
    }
    $seen = @{}
    foreach ($row in $rows) {
        $fileName = [IO.Path]::GetFileName([string]$row.file)
        if ($ExpectedFileNames -notcontains $fileName -or $seen.ContainsKey($fileName)) {
            throw "$Label evidence contains an unexpected or duplicate Flow"
        }
        if ([string]$row.flow_sha256 -ne [string]$currentFlowHashes[$fileName]) {
            throw "$Label evidence Flow hash is stale: $fileName"
        }
        $seen[$fileName] = $true
    }
}

$sourceAuthoringEvidence = Join-Path $Source $AuthoringEvidenceRelativePath
if (-not (Test-Path -LiteralPath $sourceAuthoringEvidence -PathType Leaf)) {
    throw "Missing authoritative authoring evidence: $AuthoringEvidenceRelativePath"
}
$sourceAuthoringReport = Get-Content -LiteralPath $sourceAuthoringEvidence -Raw | ConvertFrom-Json
if (
    $sourceAuthoringReport.contract_version -ne "langflow.http.authoring-e2e.validation.v2" -or
    $sourceAuthoringReport.model -ne "gemini-3.5-flash-lite" -or
    $sourceAuthoringReport.domain_id -ne "order_sales" -or
    $sourceAuthoringReport.fresh_environment -ne $true -or
    @($sourceAuthoringReport.cycles).Count -ne 4 -or
    [int]$sourceAuthoringReport.draft_llm_calls -ne 1 -or
    [int]$sourceAuthoringReport.annotation_llm_calls -ne 1 -or
    [int]$sourceAuthoringReport.repair_llm_calls -ne 0 -or
    $sourceAuthoringReport.source_text_persisted -ne $false -or
    $sourceAuthoringReport.provider_output_persisted -ne $false -or
    $sourceAuthoringReport.approval_payload_persisted -ne $false -or
    $sourceAuthoringReport.secrets_persisted -ne $false -or
    $sourceAuthoringReport.all_passed -ne $true
) {
    throw "Authoritative authoring evidence is not an exact PASS"
}
Assert-ImportEvidenceCurrent `
    -Imports $sourceAuthoringReport.imports `
    -ExpectedFileNames $AuthoringFlowNames `
    -Label "Authoring"
$sourceOrderSalesEvidence = Join-Path $Source $OrderSalesEvidenceRelativePath
if (-not (Test-Path -LiteralPath $sourceOrderSalesEvidence -PathType Leaf)) {
    throw "Missing authoritative order-sales evidence: $OrderSalesEvidenceRelativePath"
}
$sourceOrderSalesReport = Get-Content -LiteralPath $sourceOrderSalesEvidence -Raw | ConvertFrom-Json
if (
    $sourceOrderSalesReport.contract_version -ne "langflow.http.order-sales.validation.v1" -or
    $sourceOrderSalesReport.domain_id -ne "order_sales" -or
    [int]$sourceOrderSalesReport.case_count -ne 3 -or
    [int]$sourceOrderSalesReport.passed -ne 3 -or
    [int]$sourceOrderSalesReport.failed -ne 0 -or
    $sourceOrderSalesReport.source_payload_persisted -ne $false -or
    $sourceOrderSalesReport.raw_http_responses_persisted -ne $false -or
    $sourceOrderSalesReport.secrets_persisted -ne $false -or
    $sourceOrderSalesReport.all_passed -ne $true
) {
    throw "Authoritative order-sales evidence is not an exact PASS"
}
if (
    [IO.Path]::GetFileName([string]$sourceOrderSalesReport.flow_file) -ne $DataAnalysisFlowName -or
    [string]$sourceOrderSalesReport.flow_sha256 -ne [string]$currentFlowHashes[$DataAnalysisFlowName]
) {
    throw "Authoritative order-sales evidence Flow hash is stale"
}
$sourceMigrationEvidence = Join-Path $Source $MigrationEvidenceRelativePath
if (-not (Test-Path -LiteralPath $sourceMigrationEvidence -PathType Leaf)) {
    throw "Missing authoritative migration evidence: $MigrationEvidenceRelativePath"
}
$sourceMigrationReport = Get-Content -LiteralPath $sourceMigrationEvidence -Raw | ConvertFrom-Json
if (
    $sourceMigrationReport.contract_version -ne "langflow.http.migration-patches-e2e.validation.v1" -or
    $sourceMigrationReport.model -ne "gemini-3.5-flash-lite" -or
    $sourceMigrationReport.domain_id -ne "manufacturing" -or
    $sourceMigrationReport.fresh_environment -ne $true -or
    @($sourceMigrationReport.cycles).Count -ne 3 -or
    $sourceMigrationReport.revision_chain_exact -ne $true -or
    [int]$sourceMigrationReport.draft_llm_calls -ne 1 -or
    [int]$sourceMigrationReport.repair_llm_calls -ne 0 -or
    $sourceMigrationReport.dataset_patch_checks.passed -ne $true -or
    $sourceMigrationReport.data_analysis.all_passed -ne $true -or
    [int]$sourceMigrationReport.data_analysis.case_count -ne 4 -or
    [int]$sourceMigrationReport.data_analysis.passed -ne 4 -or
    [int]$sourceMigrationReport.data_analysis.failed -ne 0 -or
    $sourceMigrationReport.data_analysis.multiturn_state_progression -ne $true -or
    $sourceMigrationReport.source_text_persisted -ne $false -or
    $sourceMigrationReport.provider_output_persisted -ne $false -or
    $sourceMigrationReport.approval_payload_persisted -ne $false -or
    $sourceMigrationReport.secrets_persisted -ne $false -or
    $sourceMigrationReport.data_analysis.prompts_persisted -ne $false -or
    $sourceMigrationReport.data_analysis.raw_langflow_responses_persisted -ne $false -or
    $sourceMigrationReport.data_analysis.secrets_persisted -ne $false -or
    $sourceMigrationReport.all_passed -ne $true
) {
    throw "Authoritative migration evidence is not an exact PASS"
}
Assert-ImportEvidenceCurrent `
    -Imports $sourceMigrationReport.imports `
    -ExpectedFileNames $AuthoringFlowNames `
    -Label "Migration authoring"
if (
    [string]$sourceMigrationReport.data_analysis_flow_sha256 -ne
    [string]$currentFlowHashes[$DataAnalysisFlowName]
) {
    throw "Authoritative migration Data Analysis Flow hash is stale"
}

if (-not (Test-Path -LiteralPath $TargetFull)) {
    New-Item -ItemType Directory -Path $TargetFull | Out-Null
}

$excludedDirectoryNames = @(".pytest_cache", "__pycache__", ".ruff_cache", ".venv")

function Test-ExcludedDirectoryName {
    param([string]$Name)
    return (
        $excludedDirectoryNames -contains $Name -or
        $Name -like ".pytest_cache*" -or
        $Name -like "langflow_*_profile" -or
        $Name -like "live_v5_migration*" -or
        $Name -like "live_v6_activation*" -or
        $Name -like ".pytest_tmp*" -or
        $Name -like ".pytest_release_*" -or
        $Name -like "pytest_tmp*"
    )
}

function Test-ExcludedRelativeFilePath {
    param([string]$RelativePath)
    $normalized = $RelativePath.Replace("/", "\")
    if ($normalized.StartsWith("validation_outputs\", [StringComparison]::OrdinalIgnoreCase)) {
        return $PublishedValidationEvidence -notcontains $normalized
    }
    return (
        ($normalized -like "validation_outputs\langflow_http_authoring*.json" -and
            $normalized -ne $AuthoringEvidenceRelativePath) -or
        ($normalized -like "validation_outputs\langflow_http_order_sales*.json" -and
            $normalized -ne $OrderSalesEvidenceRelativePath) -or
        ($normalized -like "validation_outputs\langflow_http_migration*.json" -and
            $normalized -ne $MigrationEvidenceRelativePath)
    )
}

function Copy-CleanTree {
    param([string]$From, [string]$To)

    if (-not (Test-Path -LiteralPath $To)) {
        New-Item -ItemType Directory -Path $To | Out-Null
    }
    foreach ($item in Get-ChildItem -LiteralPath $From -Force) {
        if ($item.PSIsContainer) {
            if (Test-ExcludedDirectoryName -Name $item.Name) {
                continue
            }
            $relativeDirectory = $item.FullName.Substring($Source.Length + 1).Replace("/", "\")
            if ($relativeDirectory.StartsWith("validation_outputs\", [StringComparison]::OrdinalIgnoreCase)) {
                continue
            }
            Copy-CleanTree -From $item.FullName -To (Join-Path $To $item.Name)
        }
        else {
            $relative = $item.FullName.Substring($Source.Length + 1)
            if (Test-ExcludedRelativeFilePath -RelativePath $relative) {
                continue
            }
            Copy-Item -LiteralPath $item.FullName -Destination (Join-Path $To $item.Name) -Force
        }
    }
}

Copy-CleanTree -From $Source -To $TargetFull

# A previous overlay may already have copied isolated Langflow profiles or
# non-authoritative migration diagnostics. Remove only the explicitly named
# managed directories below the validated publish target.
$targetPrefix = $TargetFull.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
foreach ($managedDirectory in @(
    Get-ChildItem -LiteralPath $TargetFull -Recurse -Directory -Force |
        Where-Object {
            $_.Name -like ".pytest_cache*" -or
            $_.Name -eq "__pycache__" -or
            $_.Name -eq ".ruff_cache" -or
            $_.Name -like "langflow_*_profile" -or
            $_.Name -like "live_v5_migration*" -or
            $_.Name -like "live_v6_activation*" -or
            $_.Name -like ".pytest_tmp*" -or
            $_.Name -like ".pytest_release_*" -or
            $_.Name -like "pytest_tmp*"
        } |
        Sort-Object { $_.FullName.Length } -Descending
)) {
    $managedPath = [IO.Path]::GetFullPath($managedDirectory.FullName)
    if (-not $managedPath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing managed-directory cleanup outside target: $managedPath"
    }
    if (Test-Path -LiteralPath $managedPath -PathType Container) {
        Remove-Item -LiteralPath $managedPath -Recurse -Force
    }
}
$targetValidationOutputs = Join-Path $TargetFull "validation_outputs"
if (Test-Path -LiteralPath $targetValidationOutputs -PathType Container) {
    foreach ($profileDirectory in Get-ChildItem -LiteralPath $targetValidationOutputs -Directory -Force) {
        if (
            $profileDirectory.Name -notlike "langflow_*_profile" -and
            $profileDirectory.Name -notlike "live_v5_migration*" -and
            $profileDirectory.Name -notlike "live_v6_activation*"
        ) {
            continue
        }
        $profilePath = [IO.Path]::GetFullPath($profileDirectory.FullName)
        if (-not $profilePath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing runtime-profile cleanup outside target: $profilePath"
        }
        Remove-Item -LiteralPath $profilePath -Recurse -Force
    }
    foreach ($authoringReport in Get-ChildItem -LiteralPath $targetValidationOutputs -File -Force -Filter "langflow_http_authoring*.json") {
        if ($authoringReport.Name -eq $AuthoringEvidenceName) {
            continue
        }
        $reportPath = [IO.Path]::GetFullPath($authoringReport.FullName)
        if (-not $reportPath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing authoring-report cleanup outside target: $reportPath"
        }
        Remove-Item -LiteralPath $reportPath -Force
    }
    foreach ($orderSalesReport in Get-ChildItem -LiteralPath $targetValidationOutputs -File -Force -Filter "langflow_http_order_sales*.json") {
        if ($orderSalesReport.Name -eq $OrderSalesEvidenceName) {
            continue
        }
        $reportPath = [IO.Path]::GetFullPath($orderSalesReport.FullName)
        if (-not $reportPath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing order-sales-report cleanup outside target: $reportPath"
        }
        Remove-Item -LiteralPath $reportPath -Force
    }
    foreach ($migrationReport in Get-ChildItem -LiteralPath $targetValidationOutputs -File -Force -Filter "langflow_http_migration*.json") {
        if ($migrationReport.Name -eq $MigrationEvidenceName) {
            continue
        }
        $reportPath = [IO.Path]::GetFullPath($migrationReport.FullName)
        if (-not $reportPath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing migration-report cleanup outside target: $reportPath"
        }
        Remove-Item -LiteralPath $reportPath -Force
    }
    foreach ($validationFile in Get-ChildItem -LiteralPath $targetValidationOutputs -Recurse -File -Force) {
        $relativePath = $validationFile.FullName.Substring($TargetFull.Length + 1)
        if (-not (Test-ExcludedRelativeFilePath -RelativePath $relativePath)) {
            continue
        }
        $filePath = [IO.Path]::GetFullPath($validationFile.FullName)
        if (-not $filePath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing validation-evidence cleanup outside target: $filePath"
        }
        Remove-Item -LiteralPath $filePath -Force
    }
    foreach ($validationDirectory in @(
        Get-ChildItem -LiteralPath $targetValidationOutputs -Recurse -Directory -Force |
            Sort-Object { $_.FullName.Length } -Descending
    )) {
        $directoryPath = [IO.Path]::GetFullPath($validationDirectory.FullName)
        if (-not $directoryPath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing validation-directory cleanup outside target: $directoryPath"
        }
        Remove-Item -LiteralPath $directoryPath -Recurse -Force
    }
}

# This file belonged only to the early single-node v6 prototype. The current
# implementation has 18 capability-scoped standalone components, so retaining
# it after an overlay publish would create a duplicate Langflow implementation.
$obsoleteManagedFiles = @(
    "langflow_components\data_analysis\00_trusted_analysis_engine.py"
)
foreach ($relativePath in $obsoleteManagedFiles) {
    $obsoletePath = [IO.Path]::GetFullPath((Join-Path $TargetFull $relativePath))
    if (-not $obsoletePath.StartsWith($targetPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing obsolete-file cleanup outside target: $obsoletePath"
    }
    if (Test-Path -LiteralPath $obsoletePath -PathType Leaf) {
        Remove-Item -LiteralPath $obsoletePath -Force
    }
}

function Add-CleanFilesToMap {
    param(
        [string]$CurrentPath,
        [string]$ResolvedBase,
        [hashtable]$Result
    )

    foreach ($item in Get-ChildItem -LiteralPath $CurrentPath -Force) {
        if ($item.PSIsContainer) {
            # Skip an excluded directory before recursing into it. Some pytest
            # cache directories deliberately have restrictive ACLs, and a
            # broad `Get-ChildItem -Recurse` would fail before the later path
            # filter had a chance to exclude them.
            if (Test-ExcludedDirectoryName -Name $item.Name) {
                continue
            }
            Add-CleanFilesToMap `
                -CurrentPath $item.FullName `
                -ResolvedBase $ResolvedBase `
                -Result $Result
            continue
        }

        $relative = $item.FullName.Substring($ResolvedBase.Length + 1)
        if (Test-ExcludedRelativeFilePath -RelativePath $relative) {
            continue
        }
        $Result[$relative] = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    }
}

function Get-CleanFileMap {
    param([string]$BasePath)

    $resolvedBase = [IO.Path]::GetFullPath($BasePath).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $result = @{}
    Add-CleanFilesToMap -CurrentPath $resolvedBase -ResolvedBase $resolvedBase -Result $result
    return $result
}

$sourceFiles = Get-CleanFileMap -BasePath $Source
$targetFiles = Get-CleanFileMap -BasePath $TargetFull
$sourceOnly = @($sourceFiles.Keys | Where-Object { -not $targetFiles.ContainsKey($_) })
$targetOnly = @($targetFiles.Keys | Where-Object { -not $sourceFiles.ContainsKey($_) })
$hashMismatch = @(
    $sourceFiles.Keys |
        Where-Object { $targetFiles.ContainsKey($_) -and $sourceFiles[$_] -ne $targetFiles[$_] }
)
if ($sourceOnly.Count -or $targetOnly.Count -or $hashMismatch.Count) {
    throw (
        "Published tree mismatch: source_only={0}, target_only={1}, hash_mismatch={2}" -f
        $sourceOnly.Count, $targetOnly.Count, $hashMismatch.Count
    )
}

$sourceEnv = Get-FileHash -LiteralPath (Join-Path $Source ".env") -Algorithm SHA256
$targetEnv = Get-FileHash -LiteralPath (Join-Path $TargetFull ".env") -Algorithm SHA256
$flowCount = @(Get-ChildItem -LiteralPath (Join-Path $TargetFull "flow_exports") -Filter "*_standalone.json").Count
$targetAuthoringEvidence = Join-Path $TargetFull $AuthoringEvidenceRelativePath
$targetOrderSalesEvidence = Join-Path $TargetFull $OrderSalesEvidenceRelativePath
$targetMigrationEvidence = Join-Path $TargetFull $MigrationEvidenceRelativePath

if ($sourceEnv.Hash -ne $targetEnv.Hash) {
    throw ".env hash mismatch after copy"
}
if ($flowCount -ne 5) {
    throw "Expected 5 standalone Flow exports, found $flowCount"
}
$targetAuthoringReport = Get-Content -LiteralPath $targetAuthoringEvidence -Raw | ConvertFrom-Json
if (
    $targetAuthoringReport.contract_version -ne "langflow.http.authoring-e2e.validation.v2" -or
    $targetAuthoringReport.model -ne "gemini-3.5-flash-lite" -or
    $targetAuthoringReport.domain_id -ne "order_sales" -or
    $targetAuthoringReport.fresh_environment -ne $true -or
    @($targetAuthoringReport.cycles).Count -ne 4 -or
    [int]$targetAuthoringReport.draft_llm_calls -ne 1 -or
    [int]$targetAuthoringReport.annotation_llm_calls -ne 1 -or
    [int]$targetAuthoringReport.repair_llm_calls -ne 0 -or
    $targetAuthoringReport.source_text_persisted -ne $false -or
    $targetAuthoringReport.provider_output_persisted -ne $false -or
    $targetAuthoringReport.approval_payload_persisted -ne $false -or
    $targetAuthoringReport.secrets_persisted -ne $false -or
    $targetAuthoringReport.all_passed -ne $true
) {
    throw "Published authoring evidence is not an exact PASS"
}
$targetOrderSalesReport = Get-Content -LiteralPath $targetOrderSalesEvidence -Raw | ConvertFrom-Json
if (
    $targetOrderSalesReport.contract_version -ne "langflow.http.order-sales.validation.v1" -or
    $targetOrderSalesReport.domain_id -ne "order_sales" -or
    [int]$targetOrderSalesReport.case_count -ne 3 -or
    [int]$targetOrderSalesReport.passed -ne 3 -or
    [int]$targetOrderSalesReport.failed -ne 0 -or
    $targetOrderSalesReport.source_payload_persisted -ne $false -or
    $targetOrderSalesReport.raw_http_responses_persisted -ne $false -or
    $targetOrderSalesReport.secrets_persisted -ne $false -or
    $targetOrderSalesReport.all_passed -ne $true
) {
    throw "Published order-sales evidence is not an exact PASS"
}
$targetMigrationReport = Get-Content -LiteralPath $targetMigrationEvidence -Raw | ConvertFrom-Json
if (
    $targetMigrationReport.contract_version -ne "langflow.http.migration-patches-e2e.validation.v1" -or
    $targetMigrationReport.model -ne "gemini-3.5-flash-lite" -or
    $targetMigrationReport.domain_id -ne "manufacturing" -or
    $targetMigrationReport.fresh_environment -ne $true -or
    @($targetMigrationReport.cycles).Count -ne 3 -or
    $targetMigrationReport.revision_chain_exact -ne $true -or
    [int]$targetMigrationReport.draft_llm_calls -ne 1 -or
    [int]$targetMigrationReport.repair_llm_calls -ne 0 -or
    $targetMigrationReport.dataset_patch_checks.passed -ne $true -or
    $targetMigrationReport.data_analysis.all_passed -ne $true -or
    [int]$targetMigrationReport.data_analysis.case_count -ne 4 -or
    [int]$targetMigrationReport.data_analysis.passed -ne 4 -or
    [int]$targetMigrationReport.data_analysis.failed -ne 0 -or
    $targetMigrationReport.data_analysis.multiturn_state_progression -ne $true -or
    $targetMigrationReport.source_text_persisted -ne $false -or
    $targetMigrationReport.provider_output_persisted -ne $false -or
    $targetMigrationReport.approval_payload_persisted -ne $false -or
    $targetMigrationReport.secrets_persisted -ne $false -or
    $targetMigrationReport.data_analysis.prompts_persisted -ne $false -or
    $targetMigrationReport.data_analysis.raw_langflow_responses_persisted -ne $false -or
    $targetMigrationReport.data_analysis.secrets_persisted -ne $false -or
    $targetMigrationReport.all_passed -ne $true
) {
    throw "Published migration evidence is not an exact PASS"
}

[pscustomobject]@{
    Source = $Source
    Target = $TargetFull
    EnvHashMatched = $true
    FlowCount = $flowCount
    AuthoringEvidence = $AuthoringEvidenceRelativePath
    OrderSalesEvidence = $OrderSalesEvidenceRelativePath
    MigrationEvidence = $MigrationEvidenceRelativePath
    FileCount = $sourceFiles.Count
    TreeHashMatched = $true
} | ConvertTo-Json
