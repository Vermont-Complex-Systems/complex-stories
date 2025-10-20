import * as v from 'valibot'

// Base annotation schema matching the AcademicResearchGroups model
export const annotationSchema = v.object({
	id: v.number(),
	payroll_name: v.string(),
	payroll_year: v.number(),
	position: v.optional(v.nullable(v.string())),
	oa_display_name: v.optional(v.nullable(v.string())),
	is_prof: v.optional(v.nullable(v.boolean())),
	perceived_as_male: v.optional(v.nullable(v.boolean())),
	host_dept: v.optional(v.nullable(v.string())),
	has_research_group: v.optional(v.nullable(v.boolean())),
	group_size: v.optional(v.nullable(v.number())),
	oa_uid: v.optional(v.nullable(v.string())),
	group_url: v.optional(v.nullable(v.string())),
	first_pub_year: v.optional(v.nullable(v.number())),
	inst_ipeds_id: v.optional(v.nullable(v.string())),
	notes: v.optional(v.nullable(v.string())),
	college: v.optional(v.nullable(v.string())),
})

// Create annotation schema (without id, since it's auto-generated)
export const createAnnotationSchema = v.object({
	payroll_name: v.pipe(v.string(), v.minLength(1, 'Payroll name is required')),
	payroll_year: v.pipe(v.number(), v.minValue(1900), v.maxValue(2100)),
	position: v.optional(v.nullable(v.string())),
	oa_display_name: v.optional(v.nullable(v.string())),
	is_prof: v.optional(v.nullable(v.boolean())),
	perceived_as_male: v.optional(v.nullable(v.boolean())),
	host_dept: v.optional(v.nullable(v.string())),
	has_research_group: v.optional(v.nullable(v.boolean())),
	group_size: v.optional(v.nullable(v.pipe(v.number(), v.minValue(0)))),
	oa_uid: v.optional(v.nullable(v.string())),
	group_url: v.optional(v.nullable(v.pipe(v.string(), v.url('Must be a valid URL')))),
	first_pub_year: v.optional(v.nullable(v.pipe(v.number(), v.minValue(1900), v.maxValue(2100)))),
	inst_ipeds_id: v.optional(v.nullable(v.string())),
	notes: v.optional(v.nullable(v.string())),
	college: v.optional(v.nullable(v.string())),
})

// Update annotation schema (all fields optional except id for identification)
export const updateAnnotationSchema = v.object({
	id: v.pipe(v.number(), v.minValue(1, 'Record ID is required')),
	payroll_name: v.optional(v.nullable(v.string())),
	payroll_year: v.optional(v.nullable(v.pipe(v.number(), v.minValue(1900), v.maxValue(2100)))),
	position: v.optional(v.nullable(v.string())),
	oa_display_name: v.optional(v.nullable(v.string())),
	is_prof: v.optional(v.nullable(v.boolean())),
	perceived_as_male: v.optional(v.nullable(v.boolean())),
	host_dept: v.optional(v.nullable(v.string())),
	has_research_group: v.optional(v.nullable(v.boolean())),
	group_size: v.optional(v.nullable(v.pipe(v.number(), v.minValue(0)))),
	group_url: v.optional(v.nullable(v.pipe(v.string(), v.url('Must be a valid URL')))),
	first_pub_year: v.optional(v.nullable(v.pipe(v.number(), v.minValue(1900), v.maxValue(2100)))),
	inst_ipeds_id: v.optional(v.nullable(v.string())),
	notes: v.optional(v.nullable(v.string())),
	college: v.optional(v.nullable(v.string())),
})

// Delete annotation schema (just need id)
export const deleteAnnotationSchema = v.object({
	id: v.pipe(v.number(), v.minValue(1, 'Record ID is required')),
})

// Filter schema for getting annotations
export const filterAnnotationsSchema = v.optional(v.object({
	skip: v.optional(v.pipe(v.number(), v.minValue(0))),
	limit: v.optional(v.pipe(v.number(), v.minValue(1), v.maxValue(1000))),
	payroll_year: v.optional(v.nullable(v.number())),
}))

// Bulk create schema
export const bulkCreateAnnotationsSchema = v.array(createAnnotationSchema)

// Type exports
export type Annotation = v.InferOutput<typeof annotationSchema>
export type CreateAnnotation = v.InferOutput<typeof createAnnotationSchema>
export type UpdateAnnotation = v.InferOutput<typeof updateAnnotationSchema>
export type DeleteAnnotation = v.InferOutput<typeof deleteAnnotationSchema>
export type FilterAnnotations = v.InferOutput<typeof filterAnnotationsSchema>
export type BulkCreateAnnotations = v.InferOutput<typeof bulkCreateAnnotationsSchema>