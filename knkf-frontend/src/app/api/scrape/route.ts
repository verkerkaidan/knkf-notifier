import { exec } from "child_process";
import { type NextRequest, NextResponse } from "next/server";
import path from "path";
import { promisify } from "util";

const execAsync = promisify(exec);

export const dynamic = "force-dynamic";
export const maxDuration = 60; // Allow up to 60 seconds for scraping

interface ScrapeResponse {
	success: boolean;
	message: string;
	count?: number;
	error?: string;
}

// Simple in-memory rate limiting
let lastScrapeTime = 0;
const RATE_LIMIT_MS = 60000; // 1 minute between scrapes

export async function POST(
	request: NextRequest,
): Promise<NextResponse<ScrapeResponse>> {
	// Rate limiting: prevent scraping more than once per minute
	const now = Date.now();
	if (now - lastScrapeTime < RATE_LIMIT_MS) {
		const waitTime = Math.ceil((RATE_LIMIT_MS - (now - lastScrapeTime)) / 1000);
		return NextResponse.json(
			{
				success: false,
				message: `Rate limit: Please wait ${waitTime} seconds before scraping again`,
				error: "RATE_LIMIT",
			},
			{ status: 429 },
		);
	}

	// Basic auth check - require a secret header or API key
	// For development: you can skip this or use a simple key
	// For production: implement proper authentication (NextAuth, etc.)
	const authHeader = request.headers.get("x-api-key");
	const expectedKey = process.env.SCRAPE_API_KEY;

	// Only enforce auth if SCRAPE_API_KEY is set (optional for local dev)
	if (expectedKey && authHeader !== expectedKey) {
		return NextResponse.json(
			{
				success: false,
				message: "Unauthorized: Invalid or missing API key",
				error: "UNAUTHORIZED",
			},
			{ status: 401 },
		);
	}

	try {
		// Update last scrape time
		lastScrapeTime = now;

		// Get the path to the backend directory
		const backendPath = path.join(process.cwd(), "..", "knkf-backend");

		// Get the Python virtual environment path
		const venvPython = path.join(process.cwd(), "..", ".venv", "bin", "python");

		// Validate paths exist and are within expected locations (prevent path traversal)
		if (
			!backendPath.includes("knkf-backend") ||
			!venvPython.includes(".venv")
		) {
			throw new Error("Invalid paths detected");
		}

		// Execute the scraper with database save
		// Using template literals with validated paths (no user input)
		const command = `cd "${backendPath}" && "${venvPython}" main.py`;

		console.log("Executing scraper command:", command);

		const { stdout, stderr } = await execAsync(command, {
			timeout: 55000, // 55 seconds timeout
		});

		console.log("Scraper stdout:", stdout);
		if (stderr) {
			console.error("Scraper stderr:", stderr);
		}

		// Parse the output to get the count
		const countMatch = stdout.match(/Total competitions found: (\d+)/);
		const dbCountMatch = stdout.match(/Saved to database: (\d+)\/(\d+)/);

		const count = dbCountMatch
			? parseInt(dbCountMatch[1])
			: countMatch
				? parseInt(countMatch[1])
				: 0;

		return NextResponse.json({
			success: true,
			message: `Successfully scraped and saved ${count} competitions`,
			count: count,
		});
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
