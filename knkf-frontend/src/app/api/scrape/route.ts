import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Allow up to 60 seconds for scraping

interface ScrapeResponse {
	success: boolean;
	message: string;
	count?: number;
	error?: string;
}

export async function POST(): Promise<NextResponse<ScrapeResponse>> {
	try {
		// Get backend API URL and key from environment
		const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "";
		const apiKey = process.env.NEXT_PUBLIC_SCRAPE_API_KEY || "";

		// Forward the request to the backend
		const res = await fetch(apiUrl, {
			method: "POST",
			headers: {
				"x-api-key": apiKey,
				"Content-Type": "application/json",
			},
		});

		const data = await res.json();
		return NextResponse.json(data, { status: res.status });
	} catch (error) {
		console.error("Scraper error:", error);
		const errorMessage =
			error instanceof Error ? error.message : "Unknown error occurred";
		return NextResponse.json(
			{
				success: false,
				message: "Failed to scrape competitions",
				error: errorMessage,
			},
			{ status: 500 },
		);
	}
}
