export default function LoadingSpinner() {
	return (
		<div className="flex items-center justify-center p-8">
			<div className="flex flex-col items-center space-y-4">
				{/* Spinner */}
				<div className="relative">
					<div className="w-12 h-12 border-4 border-gray-200 dark:border-gray-700 rounded-full animate-spin">
						<div className="absolute top-0 left-0 w-full h-full border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
					</div>
				</div>

				{/* Loading text */}
				<div className="text-center">
					<p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
						Wedstrijden laden...
					</p>
					<p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
						Even geduld alstublieft
					</p>
				</div>
			</div>
		</div>
	);
}
