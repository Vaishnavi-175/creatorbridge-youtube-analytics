# CreatorBridge – Data Dictionary

## Project Goal

CreatorBridge is an end-to-end YouTube Creator & Brand Analytics Platform.

The platform connects:

Creator → Channel → Content → Audience → Brand → Campaign → Conversion → Revenue

---

## 1. creators

Stores creator-level information.

| Column | Description |
|---|---|
| creator_id | Unique creator identifier |
| creator_name | Creator name |
| category | Creator niche/category |
| location | Creator location |
| language | Primary content language |
| email | Creator contact email |
| joined_date | Date creator joined the platform |

---

## 2. channels

Stores YouTube channel-level information.

| Column | Description |
|---|---|
| channel_id | Unique channel identifier |
| creator_id | Creator reference |
| channel_name | YouTube channel name |
| subscribers | Current subscriber count |
| total_views | Total channel views |
| total_videos | Total uploaded videos |
| channel_created_date | YouTube channel creation date |

---

## 3. videos

Stores video-level information.

| Column | Description |
|---|---|
| video_id | Unique video identifier |
| channel_id | Channel reference |
| title | Video title |
| category | Video/content category |
| video_type | Shorts or Long-form |
| upload_date | Video upload date |
| duration_minutes | Video duration |

---

## 4. video_metrics

Stores performance metrics for each video.

| Column | Description |
|---|---|
| video_id | Video reference |
| views | Number of views |
| likes | Number of likes |
| comments | Number of comments |
| shares | Number of shares |
| watch_time_hours | Total watch time |

---

## 5. audience

Stores audience demographic information.

| Column | Description |
|---|---|
| audience_id | Unique audience record |
| channel_id | Channel reference |
| age_group | Audience age group |
| gender | Audience gender |
| location | Audience location |
| audience_percentage | Percentage of audience |

---

## 6. brands

Stores brand information.

| Column | Description |
|---|---|
| brand_id | Unique brand identifier |
| brand_name | Brand name |
| category | Brand/product category |
| product | Product name |

---

## 7. campaigns

Stores campaign-level information.

| Column | Description |
|---|---|
| campaign_id | Unique campaign identifier |
| brand_id | Brand reference |
| campaign_name | Campaign name |
| product | Promoted product |
| campaign_category | Campaign category |
| budget | Campaign budget |
| start_date | Campaign start date |
| end_date | Campaign end date |

---

## 8. campaign_creators

Connects creators with campaigns.

| Column | Description |
|---|---|
| campaign_id | Campaign reference |
| creator_id | Creator reference |
| agreed_cost | Cost agreed with creator |

This table represents the many-to-many relationship between campaigns and creators.

---

## 9. campaign_performance

Stores campaign results.

| Column | Description |
|---|---|
| campaign_id | Campaign reference |
| creator_id | Creator reference |
| views | Campaign views |
| likes | Campaign likes |
| comments | Campaign comments |
| clicks | Campaign clicks |
| conversions | Number of conversions |
| revenue | Revenue generated |

---

# Core Relationships

Creator
→ Channel
→ Videos
→ Video Metrics

Channel
→ Audience

Brand
→ Campaign
→ Campaign Creators
→ Campaign Performance

---

# Planned Analytics

## Creator Analytics
- Subscriber growth
- Total views
- Average views per video
- Engagement rate
- Upload consistency
- Shorts vs Long-form performance
- Top-performing content
- Audience demographics

## Brand Analytics
- Campaign spend
- Campaign reach
- Engagement
- Click-through rate
- Conversion rate
- Revenue
- ROI

## Creator–Brand Matching
- Category relevance
- Audience alignment
- Engagement performance
- Growth trend
- Content relevance
- Campaign performance
- Budget compatibility

## Advanced Analytics
- Emerging creator detection
- Unusual growth/engagement pattern detection
- Content performance analysis
- Campaign ROI analysis
- Conversion analysis