import CompetitionsList from "@/components/CompetitionsList";

export default function Home() {
	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
			<div className="container mx-auto px-4 py-8">
				{/* Header */}
				<header className="text-center mb-12">
					<div className="flex items-center justify-center mb-4">
						<div className="text-4xl mr-3">🏋️‍♀️</div>
						<h1 className="text-4xl font-bold text-gray-800 dark:text-white">
							Aidans KNKF Kalender
						</h1>
					</div>
					<p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
						Op deze pagina vind je een overzicht van alle aankomende
						powerlifting meets in Nederland, georganiseerd door de KNKF.
					</p>
					<p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
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
