interface Competition {
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
}

interface CompetitionCardProps {
	competition: Competition;
}

export default function CompetitionCard({ competition }: CompetitionCardProps) {
	const formatDate = (dateString: string) => {
		const date = new Date(dateString);
		return date.toLocaleDateString("nl-NL", {
			day: "numeric",
			month: "long",
			year: "numeric",
		});
	};

	const formatDateRange = (startDate: string, endDate: string) => {
		if (startDate === endDate) {
			return formatDate(startDate);
		}

		const start = new Date(startDate);
		const end = new Date(endDate);

		if (
			start.getMonth() === end.getMonth() &&
			start.getFullYear() === end.getFullYear()
		) {
			return `${start.getDate()} - ${end.getDate()} ${end.toLocaleDateString("nl-NL", { month: "long", year: "numeric" })}`;
		}

		return `${formatDate(startDate)} - ${formatDate(endDate)}`;
	};

	const getTypeColor = (type: string) => {
		switch (type.toLowerCase()) {
			case "classic":
				return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
			case "equipped":
				return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
			case "beginner":
				return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
			default:
				return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
		}
	};

	const getStatusColor = (status: string) => {
		if (status.toLowerCase().includes("definitief")) {
			return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
		}
		if (status.toLowerCase().includes("indicatie")) {
			return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
		}
		return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
	};

	return (
		<div className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-200 dark:border-gray-700">
			{/* Header */}
			<div className="p-6 pb-4">
				<div className="flex items-start justify-between mb-3">
					<h3 className="text-lg font-bold text-gray-900 dark:text-white line-clamp-2 flex-1">
						{competition.name}
					</h3>
					{competition.qualification_required && (
						<span className="ml-2 inline-block">👑</span>
					)}
				</div>

				{/* Date */}
				<div className="flex items-center text-gray-600 dark:text-gray-300 mb-2">
					<span className="text-sm mr-2">📅</span>
					<span className="text-sm font-medium">
						{formatDateRange(competition.start_date, competition.end_date)}
					</span>
				</div>

				{/* Location */}
				<div className="flex items-center text-gray-600 dark:text-gray-300 mb-2">
					<span className="text-sm mr-2">📍</span>
					<span className="text-sm">{competition.location}</span>
				</div>

				{/* Organization */}
				<div className="flex items-center text-gray-600 dark:text-gray-300 mb-4">
					<span className="text-sm mr-2">🏢</span>
					<span className="text-sm">{competition.organization}</span>
				</div>

				{/* Tags */}
				<div className="flex flex-wrap gap-2 mb-4">
					{/* Competition Type */}
					{competition.competition_type && (
						<span
							className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(competition.competition_type)}`}
						>
							{competition.competition_type}
						</span>
					)}

					{/* Status */}
					<span
						className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(competition.status)}`}
					>
						{competition.status}
					</span>

					{/* Capacity */}
					{competition.capacity && competition.capacity !== "-" && (
						<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
							{competition.capacity} plaatsen
						</span>
					)}
				</div>

				{/* Qualification Required */}
				{competition.qualification_required && (
					<div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3 mb-4">
						<div className="flex items-center">
							<span className="text-yellow-600 dark:text-yellow-400 mr-2">
								⚠️
							</span>
							<span className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
								Kwalificatie vereist
							</span>
						</div>
					</div>
				)}
			</div>

			{/* Footer */}
			<div className="px-6 pb-6">
				{competition.url ? (
					<a
						href={competition.url}
						target="_blank"
						rel="noopener noreferrer"
						className="inline-flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 rounded-lg transition-colors duration-200"
					>
						Meer informatie
						<span className="ml-2">🔗</span>
					</a>
				) : (
					<div className="text-center py-2 text-sm text-gray-500 dark:text-gray-400">
						Meer informatie volgt binnenkort
					</div>
				)}
			</div>
		</div>
	);
}
