import { createHash } from 'crypto';

/**
 * Generates a unique ID for an article based on its link and title.
 * @param article The article object, expected to have link and title properties.
 * @returns A SHA-256 hash string.
 */
export function generateArticleId(article: { link?: string; title?: string }): string {
    const link = article.link || '';
    const title = article.title || '';
    const content = `${link}|${title}`;
    return createHash('sha256').update(content, 'utf-8').digest('hex');
}

/**
 * Generates a Discord channel name from a feed URL and an optional title.
 * @param feedUrl The URL of the RSS feed.
 * @param feedTitle An optional title for the feed.
 * @returns A sanitized, valid Discord channel name.
 */
export function getChannelNameForFeed(feedUrl: string, feedTitle?: string): string {
    let name: string;

    if (feedTitle) {
        // Generate from title
        name = feedTitle
            .toLowerCase()
            .replace(/[^\w\s-]/g, '') // Remove non-alphanumeric/space/hyphen chars
            .replace(/\s+/g, '-')      // Replace spaces with hyphens
            .replace(/-+/g, '-');      // Collapse multiple hyphens

        name = name.replace(/^-+|-+$/g, ''); // Trim leading/trailing hyphens

        // Truncate to Discord's limit (leaving room for prefix)
        if (name.length > 90) {
            name = name.substring(0, 90);
        }
        name = `rss-${name}`;
    } else {
        // Generate from URL
        try {
            const url = new URL(feedUrl);
            const domain = url.hostname.replace(/^www\./, '');
            const parts = domain.split('.');

            if (parts.length > 2) {
                // e.g., subdomain.example.co.uk -> example
                name = parts.slice(-2, -1)[0];
            } else {
                // e.g., example.com -> example
                name = parts[0];
            }
            name = `rss-${name}`;
        } catch {
            // Fallback to hash if URL is invalid
            const hash = createHash('md5').update(feedUrl, 'utf-8').digest('hex').substring(0, 8);
            name = `rss-feed-${hash}`;
        }
    }

    // Final cleanup to ensure it's valid
    if (name.length < 2) {
        const hash = createHash('md5').update(feedUrl, 'utf-8').digest('hex').substring(0, 8);
        return `rss-feed-${hash}`;
    }

    return name.substring(0, 100); // Enforce max length
}
