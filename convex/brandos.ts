import { v } from "convex/values";

import type { Doc } from "./_generated/dataModel";
import { query } from "./_generated/server";

export const activeBrand = query({
  args: {},
  returns: v.union(
    v.null(),
    v.object({
      _id: v.id("brands"),
      _creationTime: v.number(),
      sqlId: v.string(),
      name: v.optional(v.string()),
      founderName: v.optional(v.string()),
      category: v.optional(v.string()),
      signatureLine: v.optional(v.string()),
      createdAt: v.optional(v.string()),
      updatedAt: v.optional(v.string()),
    }),
  ),
  handler: async (ctx) => {
    const brand = await ctx.db
      .query("brands")
      .withIndex("by_is_active", (q) => q.eq("isActive", true))
      .first();
    if (!brand) return null;

    return {
      _id: brand._id,
      _creationTime: brand._creationTime,
      sqlId: brand.sqlId,
      name: brand.name,
      founderName: brand.founderName,
      category: brand.category,
      signatureLine: brand.signatureLine,
      createdAt: brand.createdAt,
      updatedAt: brand.updatedAt,
    };
  },
});

function toPublicIdea(idea: Doc<"ideas">) {
  return {
    _id: idea._id,
    _creationTime: idea._creationTime,
    sqlId: idea.sqlId,
    brandId: idea.brandId,
    title: idea.title,
    sourceType: idea.sourceType,
    sourceReference: idea.sourceReference,
    status: idea.status,
    totalPriorityScore: idea.totalPriorityScore,
    createdAt: idea.createdAt,
    updatedAt: idea.updatedAt,
  };
}

export const recentIdeas = query({
  args: {
    brandSqlId: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  returns: v.array(
    v.object({
      _id: v.id("ideas"),
      _creationTime: v.number(),
      sqlId: v.string(),
      brandId: v.optional(v.string()),
      title: v.optional(v.string()),
      sourceType: v.optional(v.string()),
      sourceReference: v.optional(v.string()),
      status: v.optional(v.string()),
      totalPriorityScore: v.optional(v.number()),
      createdAt: v.optional(v.string()),
      updatedAt: v.optional(v.string()),
    }),
  ),
  handler: async (ctx, args) => {
    const limit = Math.min(args.limit ?? 10, 50);
    if (args.brandSqlId) {
      const ideas = await ctx.db
        .query("ideas")
        .withIndex("by_brand_id", (q) => q.eq("brandId", args.brandSqlId))
        .order("desc")
        .take(limit);
      return ideas.map(toPublicIdea);
    }

    const ideas = await ctx.db.query("ideas").withIndex("by_sql_id").order("desc").take(limit);
    return ideas.map(toPublicIdea);
  },
});

export const migrationOverview = query({
  args: {},
  returns: v.object({
    keyTables: v.array(
      v.object({
        table: v.string(),
        hasData: v.boolean(),
        sampleSqlId: v.union(v.string(), v.null()),
      }),
    ),
  }),
  handler: async (ctx) => {
    const brand = await ctx.db.query("brands").withIndex("by_sql_id").first();
    const idea = await ctx.db.query("ideas").withIndex("by_sql_id").first();
    const content = await ctx.db.query("content_items").withIndex("by_sql_id").first();
    const memory = await ctx.db.query("memory_records").withIndex("by_sql_id").first();
    const telegram = await ctx.db
      .query("telegram_messages")
      .withIndex("by_sql_id")
      .first();

    return {
      keyTables: [
        { table: "brands", hasData: brand !== null, sampleSqlId: brand?.sqlId ?? null },
        { table: "ideas", hasData: idea !== null, sampleSqlId: idea?.sqlId ?? null },
        {
          table: "content_items",
          hasData: content !== null,
          sampleSqlId: content?.sqlId ?? null,
        },
        {
          table: "memory_records",
          hasData: memory !== null,
          sampleSqlId: memory?.sqlId ?? null,
        },
        {
          table: "telegram_messages",
          hasData: telegram !== null,
          sampleSqlId: telegram?.sqlId ?? null,
        },
      ],
    };
  },
});
