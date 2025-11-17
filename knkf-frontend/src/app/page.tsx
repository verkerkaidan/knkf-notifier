import CompetitionsList from "@/components/CompetitionsList";

export default function Home() {
	return (
		<div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900 flex flex-col items-center justify-center">
			<div className="w-full max-w-5xl mx-auto px-4 py-10 rounded-2xl border border-gray-300 dark:border-gray-800 shadow-lg">
				{/* Header */}
				<header className="text-center mb-10">
					<div className="flex items-center justify-center mb-4">
						<div className="text-3xl mr-2">🏋️‍♂️</div>
						<h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 tracking-tight">
							Aidans KNKF Kalender
						</h1>
					</div>
					<p className="text-base text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-1">
						Op deze pagina vind je een overzicht van alle aankomende
						powerlifting meets in Nederland, georganiseerd door de KNKF.
					</p>
					<p className="text-sm text-gray-500 dark:text-gray-400 max-w-xl mx-auto">
						De KNKF heeft geen mailing lijst, dus deze website functioneert als
						mijn persoonlijke mailinglijst.
					</p>
				</header>

				{/* Competitions List */}
				<CompetitionsList />
			</div>
		</div>
	);
}
