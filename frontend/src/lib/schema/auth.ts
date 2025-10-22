import * as v from 'valibot'

// User registration schema
export const registerUserSchema = v.object({
	username: v.pipe(v.string(), v.minLength(3)),
	email: v.pipe(v.string(), v.email()),
	password: v.pipe(v.string(), v.minLength(8)),
	role: v.optional(v.string(), 'annotator')
})

// User login schema
export const loginUserSchema = v.object({
	username: v.pipe(v.string(), v.minLength(1)),
	password: v.pipe(v.string(), v.minLength(1))
})

// User response schema (for TypeScript types)
export const userSchema = v.object({
	id: v.number(),
	username: v.string(),
	email: v.string(),
	role: v.string(),
	payroll_name: v.optional(v.nullable(v.string())),
	is_active: v.boolean(),
	created_at: v.string(),
	last_login: v.optional(v.nullable(v.string()))
})

// Auth token response schema
export const tokenSchema = v.object({
	access_token: v.string(),
	token_type: v.string(),
	user: userSchema
})

// Update user role schema
export const updateUserRoleSchema = v.object({
	user_id: v.number(),
	role: v.string()
})

// Change password schema
export const changePasswordSchema = v.object({
	current_password: v.pipe(v.string(), v.minLength(1)),
	new_password: v.pipe(v.string(), v.minLength(8))
})

// Type exports
export type User = v.InferOutput<typeof userSchema>
export type Token = v.InferOutput<typeof tokenSchema>
export type RegisterUser = v.InferInput<typeof registerUserSchema>
export type LoginUser = v.InferInput<typeof loginUserSchema>
export type UpdateUserRole = v.InferInput<typeof updateUserRoleSchema>
export type ChangePassword = v.InferInput<typeof changePasswordSchema>