import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// SQL migration mirror schema.
// `sqlId` preserves the original SQL primary key so we can backfill safely
// before any later Convex-native ID remap.

export default defineSchema({
  agent_runs: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    requestId: v.optional(v.string()),
    idempotencyKey: v.optional(v.string()),
    channel: v.optional(v.string()),
    intent: v.optional(v.string()),
    status: v.optional(v.string()),
    provider: v.optional(v.string()),
    modelAlias: v.optional(v.string()),
    contextPackId: v.optional(v.string()),
    skillsUsed: v.optional(v.any()),
    toolsUsed: v.optional(v.any()),
    contextLoaded: v.optional(v.any()),
    inputEnvelope: v.optional(v.any()),
    outputEnvelope: v.optional(v.any()),
    modelCost: v.optional(v.number()),
    toolCost: v.optional(v.number()),
    confidence: v.optional(v.number()),
    summary: v.optional(v.string()),
    proposedWrites: v.optional(v.any()),
    completedWrites: v.optional(v.any()),
    approvalsRequired: v.optional(v.any()),
    nextActions: v.optional(v.any()),
    error: v.optional(v.string()),
    completedAt: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_request_id", ["requestId"])
    .index("by_idempotency_key", ["idempotencyKey"])
    .index("by_status", ["status"])
    .index("by_context_pack_id", ["contextPackId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  approvals: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    actionType: v.optional(v.string()),
    targetType: v.optional(v.string()),
    targetId: v.optional(v.string()),
    requestedBy: v.optional(v.string()),
    riskLevel: v.optional(v.string()),
    costEstimate: v.optional(v.number()),
    status: v.optional(v.string()),
    context: v.optional(v.any()),
    approvedBy: v.optional(v.string()),
    decidedAt: v.optional(v.string()),
    notes: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_target_id", ["targetId"])
    .index("by_status", ["status"])
    .index("by_brand_id_and_status", ["brandId", "status"]),
  assets: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    productionPlanId: v.optional(v.string()),
    filename: v.optional(v.string()),
    storageKey: v.optional(v.string()),
    mediaType: v.optional(v.string()),
    mimeType: v.optional(v.string()),
    sizeBytes: v.optional(v.number()),
    checksumSha256: v.optional(v.string()),
    tags: v.optional(v.any()),
    people: v.optional(v.any()),
    location: v.optional(v.string()),
    orientation: v.optional(v.string()),
    qualityScore: v.optional(v.number()),
    rightsStatus: v.optional(v.string()),
    rightsNotes: v.optional(v.string()),
    originalPreserved: v.optional(v.boolean()),
    duplicateOfId: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_production_plan_id", ["productionPlanId"])
    .index("by_storage_key", ["storageKey"])
    .index("by_checksum_sha256", ["checksumSha256"])
    .index("by_duplicate_of_id", ["duplicateOfId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  audit_events: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    eventType: v.optional(v.string()),
    actor: v.optional(v.string()),
    targetType: v.optional(v.string()),
    targetId: v.optional(v.string()),
    summary: v.optional(v.string()),
    details: v.optional(v.any()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_event_type", ["eventType"])
    .index("by_target_id", ["targetId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  benchmark_contents: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    creatorId: v.optional(v.string()),
    sourceUrl: v.optional(v.string()),
    platform: v.optional(v.string()),
    title: v.optional(v.string()),
    sourceType: v.optional(v.string()),
    rawMetadata: v.optional(v.any()),
    transcriptExcerpt: v.optional(v.string()),
    hookAnalysis: v.optional(v.string()),
    structureAnalysis: v.optional(v.string()),
    visualAnalysis: v.optional(v.string()),
    editingAnalysis: v.optional(v.string()),
    transferableMechanics: v.optional(v.any()),
    protectedIdentity: v.optional(v.any()),
    mezieAdaptations: v.optional(v.any()),
    patternTags: v.optional(v.any()),
    limitations: v.optional(v.any()),
    evidenceLevel: v.optional(v.string()),
    status: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_creator_id", ["creatorId"])
    .index("by_platform", ["platform"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_platform", ["brandId", "platform"]),
  brand_document_versions: defineTable({
    sqlId: v.string(),
    brandDocumentId: v.optional(v.string()),
    versionNumber: v.optional(v.number()),
    contentMarkdown: v.optional(v.string()),
    changeSummary: v.optional(v.string()),
    checksumSha256: v.optional(v.string()),
    provenance: v.optional(v.any()),
    createdBy: v.optional(v.string()),
    approvalId: v.optional(v.string()),
    isActive: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_document_id", ["brandDocumentId"])
    .index("by_checksum_sha256", ["checksumSha256"])
    .index("by_approval_id", ["approvalId"])
    .index("by_is_active", ["isActive"]),
  brand_documents: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    documentType: v.optional(v.string()),
    title: v.optional(v.string()),
    slug: v.optional(v.string()),
    canonicalStatus: v.optional(v.string()),
    currentVersionId: v.optional(v.string()),
    sourcePath: v.optional(v.string()),
    vaultPath: v.optional(v.string()),
    sensitivity: v.optional(v.string()),
    tags: v.optional(v.any()),
    versionCount: v.optional(v.number()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_slug", ["slug"])
    .index("by_canonical_status", ["canonicalStatus"])
    .index("by_current_version_id", ["currentVersionId"])
    .index("by_brand_id_and_canonical_status", ["brandId", "canonicalStatus"]),
  brands: defineTable({
    sqlId: v.string(),
    name: v.optional(v.string()),
    founderName: v.optional(v.string()),
    category: v.optional(v.string()),
    positioning: v.optional(v.string()),
    signatureLine: v.optional(v.string()),
    isActive: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_is_active", ["isActive"]),
  calendar_events: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    title: v.optional(v.string()),
    eventType: v.optional(v.string()),
    startAt: v.optional(v.string()),
    endAt: v.optional(v.string()),
    timezone: v.optional(v.string()),
    status: v.optional(v.string()),
    capacityUnits: v.optional(v.number()),
    notes: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_event_type", ["eventType"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  capacity_plans: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    weekStart: v.optional(v.string()),
    availableHours: v.optional(v.number()),
    maxShoots: v.optional(v.number()),
    maxEdits: v.optional(v.number()),
    fallbackPlan: v.optional(v.string()),
    notes: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_week_start", ["weekStart"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  content_briefs: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    ideaId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    title: v.optional(v.string()),
    objective: v.optional(v.string()),
    audience: v.optional(v.string()),
    platform: v.optional(v.string()),
    format: v.optional(v.string()),
    pillar: v.optional(v.string()),
    series: v.optional(v.string()),
    coreMessage: v.optional(v.string()),
    audienceProblem: v.optional(v.string()),
    desiredEmotion: v.optional(v.string()),
    desiredAction: v.optional(v.string()),
    proofPoints: v.optional(v.any()),
    benchmarkReferences: v.optional(v.any()),
    visualDirection: v.optional(v.string()),
    productionConstraints: v.optional(v.any()),
    durationSeconds: v.optional(v.number()),
    cta: v.optional(v.string()),
    successMetric: v.optional(v.string()),
    evidenceStatus: v.optional(v.string()),
    status: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_idea_id", ["ideaId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_platform", ["platform"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_platform", ["brandId", "platform"])
    .index("by_brand_id_and_pillar", ["brandId", "pillar"]),
  content_items: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    ideaId: v.optional(v.string()),
    title: v.optional(v.string()),
    platform: v.optional(v.string()),
    format: v.optional(v.string()),
    pillar: v.optional(v.string()),
    series: v.optional(v.string()),
    audience: v.optional(v.string()),
    objective: v.optional(v.string()),
    status: v.optional(v.string()),
    priority: v.optional(v.string()),
    dueDate: v.optional(v.string()),
    publishAt: v.optional(v.string()),
    publishedAt: v.optional(v.string()),
    publicationUrl: v.optional(v.string()),
    readinessScore: v.optional(v.number()),
    approvalStatus: v.optional(v.string()),
    blocker: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_idea_id", ["ideaId"])
    .index("by_platform", ["platform"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_platform", ["brandId", "platform"])
    .index("by_brand_id_and_pillar", ["brandId", "pillar"]),
  context_packs: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    intent: v.optional(v.string()),
    sourceRecords: v.optional(v.any()),
    contextMarkdown: v.optional(v.string()),
    tokenEstimate: v.optional(v.number()),
    freshnessNotes: v.optional(v.any()),
    exclusions: v.optional(v.any()),
    status: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_status", ["status"])
    .index("by_brand_id_and_status", ["brandId", "status"]),
  creators: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    name: v.optional(v.string()),
    username: v.optional(v.string()),
    platform: v.optional(v.string()),
    url: v.optional(v.string()),
    category: v.optional(v.string()),
    whyTracked: v.optional(v.string()),
    tier: v.optional(v.number()),
    relevanceScore: v.optional(v.number()),
    contentPillars: v.optional(v.any()),
    formats: v.optional(v.any()),
    voice: v.optional(v.string()),
    hookStyle: v.optional(v.string()),
    productionStyle: v.optional(v.string()),
    audience: v.optional(v.string()),
    lastReviewedAt: v.optional(v.string()),
    watchStatus: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_platform", ["platform"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_platform", ["brandId", "platform"]),
  daily_briefs: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    heartbeatRunId: v.optional(v.string()),
    briefDate: v.optional(v.string()),
    title: v.optional(v.string()),
    whatChanged: v.optional(v.any()),
    creatorWatch: v.optional(v.any()),
    trendSignals: v.optional(v.any()),
    contentOpportunities: v.optional(v.any()),
    risksNoise: v.optional(v.any()),
    recommendedActions: v.optional(v.any()),
    recommendedAction: v.optional(v.string()),
    coverageGaps: v.optional(v.any()),
    vaultPath: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_heartbeat_run_id", ["heartbeatRunId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  experiments: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    title: v.optional(v.string()),
    question: v.optional(v.string()),
    hypothesis: v.optional(v.string()),
    variable: v.optional(v.string()),
    controlConditions: v.optional(v.any()),
    platform: v.optional(v.string()),
    contentType: v.optional(v.string()),
    expectedOutcome: v.optional(v.string()),
    successMetric: v.optional(v.string()),
    measurementStart: v.optional(v.string()),
    measurementEnd: v.optional(v.string()),
    status: v.optional(v.string()),
    result: v.optional(v.string()),
    interpretation: v.optional(v.string()),
    confidence: v.optional(v.number()),
    decision: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_platform", ["platform"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_platform", ["brandId", "platform"]),
  fact_checks: defineTable({
    sqlId: v.string(),
    scriptVersionId: v.optional(v.string()),
    status: v.optional(v.string()),
    claimTable: v.optional(v.any()),
    sources: v.optional(v.any()),
    unresolvedClaims: v.optional(v.any()),
    verifiedText: v.optional(v.string()),
    confidence: v.optional(v.number()),
    financialClassification: v.optional(v.string()),
    blockedClaims: v.optional(v.any()),
    riskDisclosures: v.optional(v.any()),
    reviewedBy: v.optional(v.string()),
    reviewedAt: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_script_version_id", ["scriptVersionId"])
    .index("by_status", ["status"]),
  heartbeat_runs: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    runDate: v.optional(v.string()),
    trigger: v.optional(v.string()),
    idempotencyKey: v.optional(v.string()),
    status: v.optional(v.string()),
    sourceCoverage: v.optional(v.any()),
    modelAlias: v.optional(v.string()),
    toolsUsed: v.optional(v.any()),
    modelCost: v.optional(v.number()),
    toolCost: v.optional(v.number()),
    contextPackId: v.optional(v.string()),
    recordsChanged: v.optional(v.any()),
    errors: v.optional(v.any()),
    confidence: v.optional(v.number()),
    completedAt: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_idempotency_key", ["idempotencyKey"])
    .index("by_status", ["status"])
    .index("by_context_pack_id", ["contextPackId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  heartbeat_settings: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    enabled: v.optional(v.boolean()),
    scheduleHour: v.optional(v.number()),
    timezone: v.optional(v.string()),
    mode: v.optional(v.string()),
    maxSources: v.optional(v.number()),
    maxCreators: v.optional(v.number()),
    telegramSummaryEnabled: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"]),
  hook_options: defineTable({
    sqlId: v.string(),
    scriptVersionId: v.optional(v.string()),
    text: v.optional(v.string()),
    category: v.optional(v.string()),
    clarityScore: v.optional(v.number()),
    curiosityScore: v.optional(v.number()),
    specificityScore: v.optional(v.number()),
    brandFitScore: v.optional(v.number()),
    audienceFitScore: v.optional(v.number()),
    originalityScore: v.optional(v.number()),
    totalScore: v.optional(v.number()),
    isRecommended: v.optional(v.boolean()),
    fatigueWarning: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_script_version_id", ["scriptVersionId"]),
  ideas: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    title: v.optional(v.string()),
    rawInput: v.optional(v.string()),
    sourceType: v.optional(v.string()),
    sourceReference: v.optional(v.string()),
    pillar: v.optional(v.string()),
    series: v.optional(v.string()),
    audience: v.optional(v.string()),
    platformFit: v.optional(v.any()),
    strategicObjective: v.optional(v.string()),
    urgency: v.optional(v.string()),
    status: v.optional(v.string()),
    brandFitScore: v.optional(v.number()),
    audienceValueScore: v.optional(v.number()),
    proofScore: v.optional(v.number()),
    timelinessScore: v.optional(v.number()),
    originalityScore: v.optional(v.number()),
    feasibilityScore: v.optional(v.number()),
    strategicImportanceScore: v.optional(v.number()),
    totalPriorityScore: v.optional(v.number()),
    rejectionReason: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_source_reference", ["sourceReference"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_pillar", ["brandId", "pillar"]),
  insights: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    classification: v.optional(v.string()),
    title: v.optional(v.string()),
    observation: v.optional(v.string()),
    hypothesis: v.optional(v.string()),
    evidence: v.optional(v.any()),
    confidence: v.optional(v.number()),
    status: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  memory_records: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    memoryType: v.optional(v.string()),
    title: v.optional(v.string()),
    content: v.optional(v.string()),
    canonicalStatus: v.optional(v.string()),
    confidence: v.optional(v.number()),
    provenance: v.optional(v.any()),
    vaultPath: v.optional(v.string()),
    contentChecksum: v.optional(v.string()),
    sensitivity: v.optional(v.string()),
    reviewAt: v.optional(v.string()),
    syncStatus: v.optional(v.string()),
    embeddingStatus: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_canonical_status", ["canonicalStatus"])
    .index("by_sync_status", ["syncStatus"])
    .index("by_embedding_status", ["embeddingStatus"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_canonical_status", ["brandId", "canonicalStatus"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  metric_snapshots: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    platform: v.optional(v.string()),
    capturedAt: v.optional(v.string()),
    views: v.optional(v.number()),
    impressions: v.optional(v.number()),
    engagement: v.optional(v.number()),
    saves: v.optional(v.number()),
    shares: v.optional(v.number()),
    watchTimeSeconds: v.optional(v.number()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_platform", ["platform"])
    .index("by_captured_at", ["capturedAt"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"])
    .index("by_brand_id_and_platform", ["brandId", "platform"]),
  pipeline_events: defineTable({
    sqlId: v.string(),
    contentItemId: v.optional(v.string()),
    fromStatus: v.optional(v.string()),
    toStatus: v.optional(v.string()),
    actor: v.optional(v.string()),
    reason: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_content_item_id", ["contentItemId"]),
  production_checklist_items: defineTable({
    sqlId: v.string(),
    productionPlanId: v.optional(v.string()),
    phase: v.optional(v.string()),
    label: v.optional(v.string()),
    isCritical: v.optional(v.boolean()),
    isComplete: v.optional(v.boolean()),
    completedAt: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_production_plan_id", ["productionPlanId"]),
  production_plans: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    scriptId: v.optional(v.string()),
    title: v.optional(v.string()),
    creativeTreatment: v.optional(v.string()),
    location: v.optional(v.string()),
    equipment: v.optional(v.any()),
    wardrobe: v.optional(v.any()),
    props: v.optional(v.any()),
    lightingPlan: v.optional(v.string()),
    musicDirection: v.optional(v.string()),
    scheduledAt: v.optional(v.string()),
    estimatedMinutes: v.optional(v.number()),
    status: v.optional(v.string()),
    readinessScore: v.optional(v.number()),
    blockers: v.optional(v.any()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_script_id", ["scriptId"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  production_scenes: defineTable({
    sqlId: v.string(),
    productionPlanId: v.optional(v.string()),
    sequence: v.optional(v.number()),
    title: v.optional(v.string()),
    purpose: v.optional(v.string()),
    dialogue: v.optional(v.string()),
    durationSeconds: v.optional(v.number()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_production_plan_id", ["productionPlanId"]),
  production_shots: defineTable({
    sqlId: v.string(),
    productionSceneId: v.optional(v.string()),
    sequence: v.optional(v.number()),
    framing: v.optional(v.string()),
    cameraAngle: v.optional(v.string()),
    movement: v.optional(v.string()),
    lighting: v.optional(v.string()),
    instructions: v.optional(v.string()),
    isBRoll: v.optional(v.boolean()),
    status: v.optional(v.string()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_production_scene_id", ["productionSceneId"])
    .index("by_status", ["status"]),
  proof_items: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    title: v.optional(v.string()),
    proofType: v.optional(v.string()),
    credibilityGap: v.optional(v.string()),
    context: v.optional(v.string()),
    constraints: v.optional(v.string()),
    process: v.optional(v.string()),
    output: v.optional(v.string()),
    result: v.optional(v.string()),
    lessons: v.optional(v.string()),
    evidenceLinks: v.optional(v.any()),
    assetIds: v.optional(v.any()),
    permissionStatus: v.optional(v.string()),
    sensitivity: v.optional(v.string()),
    status: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_status", ["status"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  script_versions: defineTable({
    sqlId: v.string(),
    scriptId: v.optional(v.string()),
    versionNumber: v.optional(v.number()),
    bodyText: v.optional(v.string()),
    hookSelected: v.optional(v.string()),
    onScreenText: v.optional(v.any()),
    bRollNotes: v.optional(v.any()),
    cameraNotes: v.optional(v.any()),
    cta: v.optional(v.string()),
    durationSeconds: v.optional(v.number()),
    brandAlignmentScore: v.optional(v.number()),
    originalityScore: v.optional(v.number()),
    evidenceNotes: v.optional(v.any()),
    changeSummary: v.optional(v.string()),
    checksumSha256: v.optional(v.string()),
    createdBy: v.optional(v.string()),
    approvalId: v.optional(v.string()),
    isActive: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_script_id", ["scriptId"])
    .index("by_checksum_sha256", ["checksumSha256"])
    .index("by_approval_id", ["approvalId"])
    .index("by_is_active", ["isActive"]),
  scripts: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    contentBriefId: v.optional(v.string()),
    contentItemId: v.optional(v.string()),
    title: v.optional(v.string()),
    status: v.optional(v.string()),
    currentVersionId: v.optional(v.string()),
    versionCount: v.optional(v.number()),
    factCheckStatus: v.optional(v.string()),
    financialRisk: v.optional(v.string()),
    approvalStatus: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_content_brief_id", ["contentBriefId"])
    .index("by_content_item_id", ["contentItemId"])
    .index("by_status", ["status"])
    .index("by_current_version_id", ["currentVersionId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  skill_definitions: defineTable({
    sqlId: v.string(),
    slug: v.optional(v.string()),
    name: v.optional(v.string()),
    version: v.optional(v.string()),
    description: v.optional(v.string()),
    triggerSummary: v.optional(v.string()),
    inputSchema: v.optional(v.any()),
    requiredContext: v.optional(v.any()),
    allowedTools: v.optional(v.any()),
    workflow: v.optional(v.any()),
    outputSchema: v.optional(v.any()),
    memoryPolicy: v.optional(v.string()),
    approvalPolicy: v.optional(v.string()),
    failureBehavior: v.optional(v.string()),
    modelProfile: v.optional(v.string()),
    timeoutSeconds: v.optional(v.number()),
    costClass: v.optional(v.string()),
    sourcePath: v.optional(v.string()),
    checksumSha256: v.optional(v.string()),
    enabled: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_slug", ["slug"])
    .index("by_checksum_sha256", ["checksumSha256"]),
  sync_events: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    direction: v.optional(v.string()),
    recordType: v.optional(v.string()),
    recordId: v.optional(v.string()),
    vaultPath: v.optional(v.string()),
    status: v.optional(v.string()),
    databaseChecksum: v.optional(v.string()),
    vaultChecksum: v.optional(v.string()),
    details: v.optional(v.any()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_record_id", ["recordId"])
    .index("by_status", ["status"])
    .index("by_brand_id_and_status", ["brandId", "status"]),
  tasks: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    title: v.optional(v.string()),
    dueAt: v.optional(v.string()),
    status: v.optional(v.string()),
    priority: v.optional(v.string()),
    relatedType: v.optional(v.string()),
    relatedId: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_status", ["status"])
    .index("by_related_id", ["relatedId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
  telegram_messages: defineTable({
    sqlId: v.string(),
    brandId: v.optional(v.string()),
    updateId: v.optional(v.string()),
    senderId: v.optional(v.string()),
    messageId: v.optional(v.string()),
    messageType: v.optional(v.string()),
    text: v.optional(v.string()),
    transcript: v.optional(v.string()),
    sourceReference: v.optional(v.string()),
    classification: v.optional(v.string()),
    status: v.optional(v.string()),
    createdRecordType: v.optional(v.string()),
    createdRecordId: v.optional(v.string()),
    responseText: v.optional(v.string()),
    failureReason: v.optional(v.string()),
    isDemo: v.optional(v.boolean()),
    createdAt: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  })
    .index("by_sql_id", ["sqlId"])
    .index("by_brand_id", ["brandId"])
    .index("by_update_id", ["updateId"])
    .index("by_sender_id", ["senderId"])
    .index("by_message_id", ["messageId"])
    .index("by_message_type", ["messageType"])
    .index("by_source_reference", ["sourceReference"])
    .index("by_status", ["status"])
    .index("by_created_record_id", ["createdRecordId"])
    .index("by_is_demo", ["isDemo"])
    .index("by_brand_id_and_status", ["brandId", "status"])
    .index("by_brand_id_and_is_demo", ["brandId", "isDemo"]),
});
