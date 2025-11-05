"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";

interface QueryProviderProps {
	children: React.ReactNode;
}

export default function QueryProvider({ children }: QueryProviderProps) {
	// Create a new QueryClient instance for each component tree
	// This ensures that server and client state don't interfere with each other
	const [queryClient] = useState(
		() =>
			new QueryClient({
				defaultOptions: {
					queries: {
						// With SSR, we usually want to set some default staleTime
						// above 0 to avoid refetching immediately on the client
						staleTime: 60 * 1000, // 1 minute
						gcTime: 5 * 60 * 1000, // 5 minutes (previously cacheTime)
						// Disable automatic retries for failed requests in development
						retry: (failureCount, error) => {
							// Don't retry if it's a 4xx error (client error)
							if (error instanceof Error && error.message.includes("4")) {
								return false;
							}
							// Retry up to 3 times for other errors
							return failureCount < 3;
						},
						// Don't show error notifications by default
						throwOnError: false,
					},
					mutations: {
						// Show error notifications for mutations by default
						throwOnError: true,
					},
				},
			}),
	);

	return (
		<QueryClientProvider client={queryClient}>
			{children}
			{/* Only show devtools in development */}
			{process.env.NODE_ENV === "development" && (
				<ReactQueryDevtools
					initialIsOpen={false}
					buttonPosition="bottom-right"
				/>
			)}
		</QueryClientProvider>
	);
}
