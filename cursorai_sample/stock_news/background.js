// Set up alarm to fetch news periodically
chrome.runtime.onInstalled.addListener(() => {
  // Fetch news every 30 minutes
  chrome.alarms.create('fetchNews', {
    periodInMinutes: 30
  });
});

// Listen for alarm
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'fetchNews') {
    updateBadge();
  }
});

// Update badge with number of new articles
async function updateBadge() {
  try {
    const response = await fetch(
      `https://newsapi.org/v2/everything?q=stock+market&language=ko&sortBy=publishedAt&apiKey=${NEWS_API_KEY}`
    );
    const data = await response.json();
    
    // Get last update time from storage
    const { lastUpdate } = await chrome.storage.local.get('lastUpdate');
    const now = new Date().getTime();
    
    // Count new articles since last update
    const newArticles = data.articles.filter(article => {
      const articleDate = new Date(article.publishedAt).getTime();
      return !lastUpdate || articleDate > lastUpdate;
    });
    
    // Update badge
    if (newArticles.length > 0) {
      chrome.action.setBadgeText({ text: newArticles.length.toString() });
      chrome.action.setBadgeBackgroundColor({ color: '#1a73e8' });
    }
    
    // Save current time as last update
    await chrome.storage.local.set({ lastUpdate: now });
  } catch (error) {
    console.error('Error updating badge:', error);
  }
} 