"use client";

import { useState } from "react";
import { useUpcomingCompetitions } from "@/hooks/useCompetitions";
import type { Competition } from "@/lib/supabase";
import CompetitionCard from "./CompetitionCard";
import LoadingSpinner from "./LoadingSpinner";
import ScrapeButton from "./ScrapeButton";

export default function CompetitionsList() {
	const [filter, setFilter] = useState<string>("all");

	// Use TanStack Query to fetch competitions from Supabase
	const {
		data: competitions = [],
		isLoading,
		error,
		isError,
	} = useUpcomingCompetitions();

	const filterCompetitions = (competition: Competition) => {
		if (filter === "all") return true;
		if (filter === "qualification") return competition.qualification_required;
		if (filter === "upcoming") {
			const today = new Date();
			const competitionDate = new Date(competition.start_date);
			return competitionDate > today;
		}
		return competition.competition_type.toLowerCase() === filter.toLowerCase();
	};

	const filteredCompetitions = competitions.filter(filterCompetitions);

	if (isLoading) {
		return <LoadingSpinner />;
	}

	if (isError) {
		return (
			<div className="text-center py-8">
				<div className="text-red-600 dark:text-red-400 mb-4">⚠️</div>
				<p className="text-gray-600 dark:text-gray-400">
					{error?.message ||
						"Er is een fout opgetreden bij het laden van de wedstrijden."}
				</p>
				<button
					type="button"
					onClick={() => window.location.reload()}
					className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
				>
					Probeer opnieuw
				</button>
			</div>
		);
	}

	// Get unique competition types for filter buttons
	const competitionTypes = [
		...new Set(competitions.map((comp) => comp.competition_type)),
	];

	return (
		<div className="max-w-5xl mx-auto px-2 py-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow">
			{/* Header */}
			<div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
				<div>
					<h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-1 tracking-tight">
						Powerlifting Wedstrijden
					</h2>
					<p className="text-sm text-gray-600 dark:text-gray-300">
						Alle komende powerlifting wedstrijden in Nederland georganiseerd
						door de KNKF.
					</p>
				</div>
				<ScrapeButton />
			</div>

			{/* Filter buttons */}
			<div className="flex flex-wrap gap-2 mb-6 justify-center">
				<button
					type="button"
					onClick={() => setFilter("all")}
					className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-gray-300 dark:border-gray-700 shadow-sm ${
						filter === "all"
							? "bg-blue-600 text-white"
							: "bg-gray-100 text-gray-700 hover:bg-blue-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-blue-900"
					}`}
				>
					Alle wedstrijden ({competitions.length})
				</button>

				<button
					type="button"
					onClick={() => setFilter("upcoming")}
					className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-gray-300 dark:border-gray-700 shadow-sm ${
						filter === "upcoming"
							? "bg-blue-600 text-white"
							: "bg-gray-100 text-gray-700 hover:bg-blue-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-blue-900"
					}`}
				>
					📅 Komende wedstrijden
				</button>

				<button
					type="button"
					onClick={() => setFilter("qualification")}
					className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-gray-300 dark:border-gray-700 shadow-sm ${
						filter === "qualification"
							? "bg-blue-600 text-white"
							: "bg-gray-100 text-gray-700 hover:bg-blue-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-blue-900"
					}`}
				>
					👑 Kwalificatie vereist
				</button>

				{competitionTypes.map((type) => (
					<button
						type="button"
						key={type}
						onClick={() => setFilter(type)}
						className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-gray-300 dark:border-gray-700 shadow-sm ${
							filter === type
								? "bg-blue-600 text-white"
								: "bg-gray-100 text-gray-700 hover:bg-blue-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-blue-900"
						}`}
					>
						{type}
					</button>
				))}
			</div>

			{/* Results count */}
			<div className="mb-4 text-center">
				<p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
					{filteredCompetitions.length} wedstrijd
					{filteredCompetitions.length !== 1 ? "en" : ""} gevonden
				</p>
			</div>

			{/* Competition grid */}
			{filteredCompetitions.length > 0 ? (
				<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{filteredCompetitions.map((competition) => (
						<CompetitionCard key={competition.id} competition={competition} />
					))}
				</div>
			) : (
				<div className="text-center py-10">
					<div className="text-gray-400 dark:text-gray-500 text-3xl mb-3">
						🔍
					</div>
					<h3 className="text-base font-semibold text-gray-800 dark:text-gray-100 mb-1">
						Geen wedstrijden gevonden
					</h3>
					<p className="text-sm text-gray-600 dark:text-gray-300">
						Probeer een andere filter of kom later terug voor nieuwe
						wedstrijden.
					</p>
				</div>
			)}
		</div>
	);
}
