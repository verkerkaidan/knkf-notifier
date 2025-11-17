# Security Considerations for the Scraper API

## Current Security Measures

### ✅ Implemented
1. **Rate Limiting**: 60-second cooldown between scrapes (in-memory)
2. **Optional API Key Authentication**: Can be enabled via environment variables
3. **Path Validation**: Prevents path traversal attacks
4. **Command Timeout**: 55-second timeout prevents hanging processes
5. **No User Input**: Command uses only hardcoded, validated paths

### ⚠️ Limitations

#### 1. **In-Memory Rate Limiting**
- **Issue**: Resets when server restarts
- **Impact**: Low for development, medium for production
- **Solution**: For production, use Redis or database-backed rate limiting

#### 2. **Optional Authentication**
- **Issue**: API is public by default (no auth required)
- **Impact**: Anyone can trigger scraping if they know the URL
- **Solution**: Enable API key authentication or implement proper user authentication

#### 3. **Command Execution**
- **Issue**: Executes shell commands (inherent risk)
- **Impact**: Mitigated by no user input and path validation
- **Solution**: Current implementation is safe, but consider containerization for extra isolation

## Security Levels

### 🟢 **Level 1: Local Development (Current Default)**
```env
# No API key needed - anyone can trigger scraper
# Rate limit: 1 request per minute
```
**Use when**: Developing locally, not exposed to internet

### 🟡 **Level 2: Basic Production**
```env
# Add to .env.local:
SCRAPE_API_KEY=<generate-secure-key>
NEXT_PUBLIC_SCRAPE_API_KEY=<same-key-as-above>
```
**Generate key**: `openssl rand -base64 32`
**Use when**: Deployed but for personal/internal use

### 🟠 **Level 3: Recommended Production**
- Use NextAuth or similar for user authentication
- Only allow authenticated admin users to trigger scrapes
- Implement database-backed rate limiting
- Add CSRF protection
- Log all scraper executions

## Enabling API Key Protection

### Step 1: Generate a secure key
```bash
openssl rand -base64 32
```

### Step 2: Add to your `.env.local`
```env
SCRAPE_API_KEY=your_generated_key_here
NEXT_PUBLIC_SCRAPE_API_KEY=your_generated_key_here
```

### Step 3: Restart your dev server
```bash
npm run dev
```

Now the scraper endpoint requires the `x-api-key` header with your key.

## Additional Production Recommendations

### 1. **Deploy Considerations**
- Set `SCRAPE_API_KEY` in your deployment environment (Vercel, etc.)
- Never commit `.env.local` to git
- Use different keys for staging/production

### 2. **Monitoring**
- Log all scraper requests (already implemented via `console.log`)
- Set up alerts for failed scrapes or rate limit violations
- Monitor resource usage

### 3. **Alternative Approaches**
- **Cron Job**: Run scraper on a schedule instead of on-demand
- **Queue System**: Use a job queue (BullMQ, etc.) for background processing
- **Serverless Function**: Use a separate serverless function with tighter security

### 4. **User Authentication** (Future Enhancement)
Instead of API keys, implement proper user auth:
```typescript
import { getServerSession } from "next-auth";

export async function POST(request: NextRequest) {
  const session = await getServerSession();
  if (!session || session.user.role !== "admin") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  // ... rest of scraper code
}
```

## Is It Safe?

### For Local Development: ✅ **YES**
- Not exposed to internet
- Rate limited
- No sensitive data exposed

### For Production (without auth): ⚠️ **MODERATE RISK**
- Anyone with URL can trigger (but rate limited)
- Could lead to unnecessary API calls to KNKF website
- Minimal security risk but potential for abuse

### For Production (with API key): ✅ **YES**
- Only authorized requests can trigger
- Rate limited
- Paths validated
- Good for small-scale production

### For High-Traffic Production: 🟡 **NEEDS IMPROVEMENT**
- Implement user authentication
- Database-backed rate limiting
- Consider cron job instead of on-demand
- Add monitoring and alerting

## Recommended Next Steps

1. **For now (local dev)**: Current setup is fine ✅
2. **Before deploying**: Enable API key protection
3. **For serious production**: Implement NextAuth with admin roles
4. **For scale**: Consider scheduled cron jobs instead of on-demand
