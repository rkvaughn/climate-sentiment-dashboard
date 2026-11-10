const MODEL_URL = 'https://huggingface.co/climatebert/distilroberta-base-climate-sentiment'
const BASE_MODEL_URL = 'https://huggingface.co/climatebert/distilroberta-base-climate-f'
const DATASET_URL = 'https://huggingface.co/datasets/climatebert/climate_sentiment'
const PAPER_URL = 'https://arxiv.org/abs/2110.12010'
const GITHUB_URL = 'https://github.com/climatebert'

function ExtLink({ href, children }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  )
}

export default function ModelInfo({ model }) {
  return (
    <section className="model-info">
      <h2>About the model: ClimateBERT</h2>

      <p>
        Every article on this dashboard is scored by{' '}
        <ExtLink href={MODEL_URL}>
          <code>{model || 'climatebert/distilroberta-base-climate-sentiment'}</code>
        </ExtLink>
        , an open-source language model from the ClimateBERT project, built specifically to read
        climate-related text.
      </p>

      <h3>How it was built</h3>
      <ol>
        <li>
          <strong>Starting point — DistilRoBERTa.</strong> A smaller, faster distilled version of
          the general-purpose RoBERTa language model.
        </li>
        <li>
          <strong>Climate pre-training — </strong>
          <ExtLink href={BASE_MODEL_URL}>ClimateBERT language model</ExtLink>. DistilRoBERTa was
          further pre-trained on a corpus of climate-related research paper abstracts, corporate
          and general news, and company reports (more than 2 million paragraphs as of the
          authors&rsquo; September 2022 update), so it learns how climate topics are actually
          discussed.
        </li>
        <li>
          <strong>Sentiment fine-tuning.</strong> A classification head was then trained on the{' '}
          <ExtLink href={DATASET_URL}>ClimateSentiment dataset</ExtLink>: expert-annotated,
          climate-related paragraphs from corporate annual reports and sustainability reports
          (1,000 training and 320 test paragraphs).
        </li>
      </ol>

      <h3>What it measures</h3>
      <p>
        ClimateBERT does not measure generic &ldquo;good news vs. bad news&rdquo; sentiment. It
        classifies text into three climate-specific classes, summarized here in plain language:
      </p>
      <ul className="model-classes">
        <li>
          <span className="class-swatch" style={{ backgroundColor: '#f97316' }} />
          <strong>Risk</strong> — text framing climate change as a threat, damage, cost, or
          exposure.
        </li>
        <li>
          <span className="class-swatch" style={{ backgroundColor: '#eab308' }} />
          <strong>Neutral</strong> — descriptive or factual climate text without a risk or
          opportunity framing.
        </li>
        <li>
          <span className="class-swatch" style={{ backgroundColor: '#84cc16' }} />
          <strong>Opportunity</strong> — text framing climate action as a benefit, solution,
          or opening.
        </li>
      </ul>
      <p className="model-note">
        The training labels were assigned by the authors and by finance and sustainable-finance
        students at Universität Zürich and Friedrich-Alexander-Universität Erlangen-Nürnberg. The
        formal annotation guidelines are in the appendix of the sentiment paper cited below.
      </p>

      <h3>How this dashboard uses it</h3>
      <ul>
        <li>
          Each article&rsquo;s headline and RSS summary (first 500 characters) is passed to the
          model, which returns a probability for each of the three classes.
        </li>
        <li>
          The article is placed in the column of its most probable class. Hover over an
          article&rsquo;s colored dot to see all three probabilities.
        </li>
        <li>
          The article&rsquo;s score is <code>P(opportunity) − P(risk)</code>, ranging from −1
          (certainly risk) to +1 (certainly opportunity).
        </li>
        <li>
          The gauge shows the average score of all articles published on the most recent day
          (UTC). A daily pipeline fetches new articles, scores them, and republishes this page.
        </li>
      </ul>

      <h3>Limitations</h3>
      <ul>
        <li>
          <strong>Domain shift.</strong> The sentiment classifier was trained on corporate
          disclosures, not journalism. News framing differs, so scores should be read as
          indicative rather than definitive.
        </li>
        <li>
          <strong>Short inputs.</strong> The authors note the model was trained on paragraphs and
          &ldquo;may not perform well on sentences.&rdquo; Headlines with short or missing
          summaries are the least reliable.
        </li>
        <li>
          <strong>Risk ≠ bad, opportunity ≠ good.</strong> A story about a new adaptation fund
          may read as opportunity; a story about rising insurance losses may read as risk. The
          gauge tracks framing, not whether events are good for the climate.
        </li>
      </ul>

      <h3>Source &amp; citation</h3>
      <ul className="model-links">
        <li>
          Model: <ExtLink href={MODEL_URL}>climatebert/distilroberta-base-climate-sentiment</ExtLink>{' '}
          on Hugging Face (Apache 2.0 license)
        </li>
        <li>
          Training data: <ExtLink href={DATASET_URL}>climatebert/climate_sentiment</ExtLink>{' '}
          (CC BY-NC-SA 4.0)
        </li>
        <li>
          Paper: Webersinke, Kraus, Bingler &amp; Leippold,{' '}
          <ExtLink href={PAPER_URL}>
            &ldquo;ClimateBERT: A Pretrained Language Model for Climate-Related Text&rdquo;
          </ExtLink>
          , Proceedings of the AAAI 2022 Fall Symposium: The Role of AI in Responding to Climate
          Challenges.
        </li>
        <li>
          Sentiment classifier described in: Bingler, Kraus, Leippold &amp; Webersinke, &ldquo;How
          Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions,
          and Reputation Risk&rdquo; (working paper, SSRN 3998435, 2023).
        </li>
        <li>
          Project code: <ExtLink href={GITHUB_URL}>github.com/climatebert</ExtLink>
        </li>
      </ul>
    </section>
  )
}
