import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
	throw new Error("Missing Supabase environment variables");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Types for our database
export interface Competition {
	id: number;
	name: string;
	location: string;
	organization: string;
	status: string;
	capacity: string;
	start_date: string;
	end_date: string;
	url: string | null;
	qualification_required: boolean;
	competition_type: string;
	created_at?: string;
	updated_at?: string;
}

// API functions
export const competitionsApi = {
	// Get all competitions
	getAll: async (): Promise<Competition[]> => {
		const { data, error } = await supabase
			.from("competitions")
			.select("*")
			.order("start_date", { ascending: true });

		if (error) {
			throw new Error(`Failed to fetch competitions: ${error.message}`);
		}

		return data || [];
	},

	// Get competitions by filter
	getByFilter: async (filter: {
		type?: string;
		qualificationRequired?: boolean;
		upcoming?: boolean;
	}): Promise<Competition[]> => {
		let query = supabase.from("competitions").select("*");

		// Apply filters
		if (filter.type && filter.type !== "all") {
			if (filter.type === "qualification") {
				query = query.eq("qualification_required", true);
			} else if (filter.type === "upcoming") {
				const today = new Date().toISOString().split("T")[0];
				query = query.gte("start_date", today);
			} else {
				query = query.ilike("competition_type", `%${filter.type}%`);
			}
		}

		query = query.order("start_date", { ascending: true });

		const { data, error } = await query;

		if (error) {
			throw new Error(`Failed to fetch competitions: ${error.message}`);
		}

		return data || [];
	},

	// Get single competition by ID
	getById: async (id: number): Promise<Competition | null> => {
		const { data, error } = await supabase
			.from("competitions")
			.select("*")
			.eq("id", id)
			.single();

		if (error) {
			if (error.code === "PGRST116") {
				return null; // No rows returned
			}
			throw new Error(`Failed to fetch competition: ${error.message}`);
		}

		return data;
	},

	// Create new competition
	create: async (
		competition: Omit<Competition, "id" | "created_at" | "updated_at">,
	): Promise<Competition> => {
		const { data, error } = await supabase
			.from("competitions")
			.insert([competition])
			.select()
			.single();

		if (error) {
			throw new Error(`Failed to create competition: ${error.message}`);
		}

		return data;
	},

	// Update competition
	update: async (
		id: number,
		updates: Partial<Competition>,
	): Promise<Competition> => {
		const { data, error } = await supabase
			.from("competitions")
			.update(updates)
			.eq("id", id)
			.select()
			.single();

		if (error) {
			throw new Error(`Failed to update competition: ${error.message}`);
		}

		return data;
	},

	// Delete competition
	delete: async (id: number): Promise<void> => {
		const { error } = await supabase.from("competitions").delete().eq("id", id);

		if (error) {
			throw new Error(`Failed to delete competition: ${error.message}`);
		}
	},
};
