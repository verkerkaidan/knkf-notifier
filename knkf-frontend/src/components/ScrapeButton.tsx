"use client";

import { useScrapeCompetitions } from "@/hooks/useCompetitions";

export default function ScrapeButton() {
	const {
		mutate: scrapeCompetitions,
		isPending,
		isSuccess,
		isError,
		error,
	} = useScrapeCompetitions();

	const handleScrape = () => {
		scrapeCompetitions();
	};

	return (
		<div className="flex flex-col items-center gap-2">
			<button
				type="button"
				onClick={handleScrape}
				disabled={isPending}
				className={`
					px-6 py-3 rounded-lg font-semibold transition-all duration-200
					${
						isPending
							? "bg-gray-400 cursor-not-allowed"
							: "bg-blue-600 hover:bg-blue-700 active:scale-95"
					}
					text-white shadow-md hover:shadow-lg
					disabled:opacity-50 disabled:cursor-not-allowed
					flex items-center gap-2
				`}
			>
				{isPending ? (
					<>
						<svg
							className="animate-spin h-5 w-5 text-white"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							aria-label="Loading"
						>
							<title>Loading</title>
							<circle
								className="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								strokeWidth="4"
							/>
							<path
								className="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							/>
						</svg>
						Aan het scrapen...
					</>
				) : (
					<>🔄 Wedstrijden bijwerken</>
				)}
			</button>

			{/* Success message */}
			{isSuccess && (
				<div className="text-green-600 dark:text-green-400 text-sm font-medium animate-fade-in">
					✅ Wedstrijden succesvol bijgewerkt!
				</div>
			)}

			{/* Error message */}
			{isError && (
				<div className="text-red-600 dark:text-red-400 text-sm font-medium animate-fade-in">
					❌ Fout: {error?.message || "Kon wedstrijden niet bijwerken"}
				</div>
			)}
		</div>
	);
}
