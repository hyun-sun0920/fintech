// News API key (replace with your actual API key)
const NEWS_API_KEY = 'YOUR_NEWS_API_KEY';
const OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY';

// Function to fetch news from NewsAPI
async function fetchNews() {
  try {
    const response = await fetch(
      `https://newsapi.org/v2/everything?q=stock+market&language=ko&sortBy=publishedAt&apiKey=${NEWS_API_KEY}`
    );
    const data = await response.json();
    return data.articles;
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
}

// Function to summarize text using OpenAI API
async function summarizeText(text) {
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [{
          role: "user",
          content: `다음 뉴스를 2-3문장으로 요약해주세요:\n\n${text}`
        }],
        max_tokens: 150
      })
    });
    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Error summarizing text:', error);
    throw error;
  }
}

// Function to create a news item element
function createNewsItem(article, summary) {
  const newsItem = document.createElement('div');
  newsItem.className = 'news-item';
  
  const title = document.createElement('a');
  title.className = 'news-title';
  title.href = article.url;
  title.target = '_blank';
  title.textContent = article.title;
  
  const summaryElement = document.createElement('div');
  summaryElement.className = 'news-summary';
  summaryElement.textContent = summary;
  
  const meta = document.createElement('div');
  meta.className = 'news-meta';
  
  const source = document.createElement('span');
  source.textContent = article.source.name;
  
  const date = document.createElement('span');
  date.textContent = new Date(article.publishedAt).toLocaleDateString('ko-KR');
  
  meta.appendChild(source);
  meta.appendChild(date);
  
  newsItem.appendChild(title);
  newsItem.appendChild(summaryElement);
  newsItem.appendChild(meta);
  
  return newsItem;
}

// Function to update the news container
async function updateNews() {
  const container = document.getElementById('newsContainer');
  container.innerHTML = '<div class="loading">뉴스를 불러오는 중...</div>';
  
  try {
    const articles = await fetchNews();
    container.innerHTML = '';
    
    for (const article of articles.slice(0, 5)) {
      const summary = await summarizeText(article.description || article.title);
      const newsItem = createNewsItem(article, summary);
      container.appendChild(newsItem);
    }
  } catch (error) {
    container.innerHTML = '<div class="error">뉴스를 불러오는데 실패했습니다.</div>';
  }
}

// Event listeners
document.addEventListener('DOMContentLoaded', updateNews);
document.getElementById('refreshButton').addEventListener('click', updateNews); 