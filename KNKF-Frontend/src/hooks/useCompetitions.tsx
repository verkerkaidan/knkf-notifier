import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type Competition, competitionsApi } from "@/lib/supabase";

// Query keys for cache management
export const competitionKeys = {
	all: ["competitions"] as const,
	lists: () => [...competitionKeys.all, "list"] as const,
	list: (filter?: CompetitionFilter) =>
		[...competitionKeys.lists(), { filter }] as const,
	details: () => [...competitionKeys.all, "detail"] as const,
	detail: (id: number) => [...competitionKeys.details(), id] as const,
};

export interface CompetitionFilter {
	type?: string;
	qualificationRequired?: boolean;
	upcoming?: boolean;
}

/**
 * Hook to fetch all competitions
 */
export function useCompetitions(filter?: CompetitionFilter) {
	return useQuery({
		queryKey: competitionKeys.list(filter),
		queryFn: () =>
			filter ? competitionsApi.getByFilter(filter) : competitionsApi.getAll(),
		staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
		gcTime: 10 * 60 * 1000, // Cache for 10 minutes (formerly cacheTime)
	});
}

/**
 * Hook to fetch a single competition by ID
 */
export function useCompetition(id: number) {
	return useQuery({
		queryKey: competitionKeys.detail(id),
		queryFn: () => competitionsApi.getById(id),
		enabled: !!id, // Only run if id is provided
		staleTime: 5 * 60 * 1000,
	});
}

/**
 * Hook to create a new competition
 */
export function useCreateCompetition() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (
			competition: Omit<Competition, "id" | "created_at" | "updated_at">,
		) => competitionsApi.create(competition),
		onSuccess: () => {
			// Invalidate and refetch competitions list
			queryClient.invalidateQueries({ queryKey: competitionKeys.lists() });
		},
	});
}

/**
 * Hook to update an existing competition
 */
export function useUpdateCompetition() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			id,
			updates,
		}: {
			id: number;
			updates: Partial<Competition>;
		}) => competitionsApi.update(id, updates),
		onSuccess: (data) => {
			// Invalidate the specific competition and the list
			queryClient.invalidateQueries({
				queryKey: competitionKeys.detail(data.id),
			});
			queryClient.invalidateQueries({ queryKey: competitionKeys.lists() });
		},
	});
}

/**
 * Hook to delete a competition
 */
export function useDeleteCompetition() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (id: number) => competitionsApi.delete(id),
		onSuccess: () => {
			// Invalidate the competitions list
			queryClient.invalidateQueries({ queryKey: competitionKeys.lists() });
		},
	});
}

/**
 * Hook to fetch upcoming competitions (convenience wrapper)
 */
export function useUpcomingCompetitions() {
	return useCompetitions({ upcoming: true });
}

/**
 * Hook to fetch qualification competitions (convenience wrapper)
 */
export function useQualificationCompetitions() {
	return useCompetitions({ qualificationRequired: true });
}
