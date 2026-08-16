# RAW DATA PROFILE

## Scope and source

- The workspace contains three real raw branch exports under data/raw: BanjaraHillsBranch.json, GachibowliBranch.json, and JubileeHillsBranch.json.
- There was no single data/raw/gmaps_reviews.json file in this workspace, so the actual raw source was profiled as the three branch-specific JSON exports.
- The raw files were not modified.

## 1. JSON structure

- Top-level structure: list
- Each list element: dictionary (review record)
- Schema is not uniform across all files: older branch exports are flatter; the Jubilee Hills export is more nested.

## 2. Review record counts

- BanjaraHillsBranch.json: 3000 records
- GachibowliBranch.json: 2016 records
- JubileeHillsBranch.json: 28259 records
- Total review records observed: 33275

## 3. All available fields

address, author, businessProfileId, categories, categoryName, cid, city, countryCode, details, engagement, fid, hotelStars, imageUrl, isAdvertisement, isLocalGuide, kgmid, language, lastEditedAt, likesCount, location, meta, name, neighborhood, originalLanguage, originalLanguageName, ownerResponse, permanentlyClosed, photos, place, placeId, postalCode, price, publishAt, publishedAt, publishedAtDate, rating, relativeDate, responseFromOwnerDate, responseFromOwnerText, reviewContext, reviewDetailedRating, reviewId, reviewImageUrls, reviewOrigin, reviewUrl, reviewerId, reviewerNumberOfReviews, reviewerPhotoUrl, reviewerUrl, reviewsCount, scrapedAt, searchString, stars, state, street, temporarilyClosed, text, textTranslated, title, totalScore, translatedLanguage, translatedLanguageName, url, visitedIn, visitedMonth, visitedYear

## 4. Data types and missing-value rates

| Field | Present | Missing rate | Observed types |
|---|---:|---:|---|
| address | 5016 | 84.93% | str:5016 |
| author | 28259 | 15.07% | dict:28259 |
| businessProfileId | 5016 | 84.93% | str:5016 |
| categories | 5016 | 84.93% | list:5016 |
| categoryName | 5016 | 84.93% | str:5016 |
| cid | 5016 | 84.93% | str:5016 |
| city | 5016 | 84.93% | str:5016 |
| countryCode | 5016 | 84.93% | str:5016 |
| details | 28259 | 15.07% | dict:28259 |
| engagement | 28259 | 15.07% | dict:28259 |
| fid | 5016 | 84.93% | str:5016 |
| hotelStars | 5016 | 84.93% | NoneType:5016 |
| imageUrl | 5016 | 84.93% | str:5016 |
| isAdvertisement | 5016 | 84.93% | bool:5016 |
| isLocalGuide | 5016 | 84.93% | bool:5016 |
| kgmid | 5016 | 84.93% | str:5016 |
| language | 33275 | 0.0% | NoneType:18623, str:14652 |
| lastEditedAt | 28259 | 15.07% | NoneType:23506, str:4753 |
| likesCount | 5016 | 84.93% | int:5016 |
| location | 5016 | 84.93% | dict:5016 |
| meta | 28259 | 15.07% | dict:28259 |
| name | 5016 | 84.93% | str:5016 |
| neighborhood | 5016 | 84.93% | str:5016 |
| originalLanguage | 33275 | 0.0% | NoneType:30885, str:2390 |
| originalLanguageName | 28259 | 15.07% | NoneType:28096, str:163 |
| ownerResponse | 28259 | 15.07% | NoneType:28259 |
| permanentlyClosed | 5016 | 84.93% | bool:5016 |
| photos | 28259 | 15.07% | list:28259 |
| place | 28259 | 15.07% | dict:28259 |
| placeId | 5016 | 84.93% | str:5016 |
| postalCode | 5016 | 84.93% | str:5016 |
| price | 5016 | 84.93% | str:5016 |
| publishAt | 5016 | 84.93% | str:5016 |
| publishedAt | 28259 | 15.07% | str:28259 |
| publishedAtDate | 5016 | 84.93% | str:5016 |
| rating | 33275 | 0.0% | int:28259, NoneType:5016 |
| relativeDate | 28259 | 15.07% | str:28259 |
| responseFromOwnerDate | 5016 | 84.93% | NoneType:5012, str:4 |
| responseFromOwnerText | 5016 | 84.93% | NoneType:5012, str:4 |
| reviewContext | 5016 | 84.93% | dict:5016 |
| reviewDetailedRating | 5016 | 84.93% | dict:5016 |
| reviewId | 33275 | 0.0% | str:33275 |
| reviewImageUrls | 5016 | 84.93% | list:5016 |
| reviewOrigin | 33275 | 0.0% | str:33275 |
| reviewUrl | 5016 | 84.93% | str:5016 |
| reviewerId | 5016 | 84.93% | str:5016 |
| reviewerNumberOfReviews | 5016 | 84.93% | int:5016 |
| reviewerPhotoUrl | 5016 | 84.93% | str:5016 |
| reviewerUrl | 5016 | 84.93% | str:5016 |
| reviewsCount | 5016 | 84.93% | int:5016 |
| scrapedAt | 5016 | 84.93% | str:5016 |
| searchString | 5016 | 84.93% | str:5016 |
| stars | 5016 | 84.93% | int:5016 |
| state | 5016 | 84.93% | str:5016 |
| street | 5016 | 84.93% | str:5016 |
| temporarilyClosed | 5016 | 84.93% | bool:5016 |
| text | 33275 | 0.0% | NoneType:21510, str:11765 |
| textTranslated | 33275 | 0.0% | NoneType:33080, str:195 |
| title | 5016 | 84.93% | str:5016 |
| totalScore | 5016 | 84.93% | float:5016 |
| translatedLanguage | 33275 | 0.0% | NoneType:33078, str:197 |
| translatedLanguageName | 28259 | 15.07% | NoneType:28096, str:163 |
| url | 33275 | 0.0% | str:33275 |
| visitedIn | 33275 | 0.0% | NoneType:33275 |
| visitedMonth | 28259 | 15.07% | NoneType:28259 |
| visitedYear | 28259 | 15.07% | NoneType:28259 |

## 5. Duplicate candidates

- reviewId: no repeated non-null values observed
- reviewUrl: no repeated non-null values observed
- url: 2 duplicated values found (examples: https://www.google.com/maps/search/?api=1&query=Mandi%20%40%2036%20Arabian%20Kitchen&query_place_id=ChIJOSpiGFiXyzsREQXAgo-lwMI:3000, https://www.google.com/maps/search/?api=1&query=Mandi%20%40%2036%20Arabian%20Kitchen&query_place_id=ChIJzTvmzbeTyzsR69-YcWo1sGY:2016)
- reviewerId: 64 duplicated values found (examples: 106162474567795635533:2, 113987760515488377947:2, 106389824133369400456:2, 111937809069941225971:2, 116121856393949007830:2)
- name: 141 duplicated values found (examples: John Marcus:2, S K:2, Shobiya Shoaib:2, Fayez Mohammed:2, Nabil Yasir:2)
- rating: 5 duplicated values found (examples: 4:8579, 5:13976, 3:2924, 1:1867, 2:913)
- stars: 5 duplicated values found (examples: 5:2481, 2:180, 3:445, 4:1309, 1:601)
- publishedAt: no repeated non-null values observed
- publishAt: 38 duplicated values found (examples: a day ago:3, 2 days ago:3, 4 days ago:3, 6 days ago:5, a week ago:22)
- responseFromOwnerDate: no repeated non-null values observed
- responseFromOwnerText: no repeated non-null values observed
- text: 243 duplicated values found (examples: Excellent:36, Very good:11, Great food:7, Good...:2, Good:205)
- placeId: 2 duplicated values found (examples: ChIJOSpiGFiXyzsREQXAgo-lwMI:3000, ChIJzTvmzbeTyzsR69-YcWo1sGY:2016)

## 6. Date fields

- `publishedAt` appears in the newer Jubilee Hills record format as an ISO-8601 timestamp.
- `publishAt` appears in older branch exports as a relative/human-readable string such as "18 hours ago" or "Edited 13 hours ago".
- `lastEditedAt` appears in Jubilee Hills records and indicates a later edit timestamp.
- `responseFromOwnerDate` appears in older flat records as a timestamp for owner response.
- `visitedIn`, `visitedYear`, and `visitedMonth` appear as contextual metadata fields in some records.

## 7. Rating fields

- `rating` is the main normalized rating field and is present in all exported record sets.
- `stars` appears in older flat exports and is likely functionally equivalent to `rating`.
- `reviewDetailedRating` appears in older flat exports and likely captures a breakdown or nested rating object; it should not be treated as a single scalar rating unless explicitly unpacked.

## 8. Review-text fields

- `text` is the primary review body field.
- `textTranslated` appears as a translation field where available.
- `language` and `translatedLanguage` provide language metadata; they do not replace the review text itself.

## 9. Branch/place identification fields

- `place` is a nested object in the Jubilee Hills export and contains the place metadata, including `name`, `placeId`, and `address`.
- `searchString` is a scraper-generated Google Maps URL/search trace and should not be used as an analytical branch identifier.
- `name` is reviewer name in older exports and should not be mistaken for branch name.
- `place.name` is the business-name field in the Jubilee Hills export; when available, it is the best raw place indicator.
- Branch identity is effectively implied by the file name and, in newer records, by nested place metadata; there is no canonical branch_id field in the raw files.

## 10. Owner-response fields

- `responseFromOwnerText` is the owner-response text in older records.
- `responseFromOwnerDate` is the owner-response timestamp in older records.
- `ownerResponse` is a nested field in Jubilee Hills records and likely contains the structured owner response object.

## 11. Reviewer-identifying fields

- `reviewerId` identifies the Google Maps reviewer profile and is retained in older flat exports.
- `reviewerUrl` and `reviewerPhotoUrl` are profile/link metadata and should be considered identifying or personal data.
- `name` is a reviewer display name in older exports.
- `author` is a nested reviewer object in newer exports and should be treated as identifying metadata unless de-identified.

## 12. Fields that should not be retained for analytics

- `searchString`
- `reviewerUrl`
- `reviewerPhotoUrl`
- `reviewImageUrls`
- `photos`
- `reviewOrigin`
- `publishAt` (older relative string form)
- `relativeDate`
- `reviewContext`
- `engagement`
- `meta`
- any raw URL, profile image, or scraper metadata that is not required for analysis

## 13. Recommended normalized schema for the analytics pipeline

The raw schema should be normalized into a lightweight review table before NLP and prediction.

- `review_id` — canonical review identifier from `reviewId` or another stable raw key
- `brand_id` — fixed brand-level identifier for ONE Mandi / Mandi @ 36 Arabian Kitchen
- `branch_id` — stable branch identifier derived from file name or place metadata
- `branch_name` — branch label derived from file name or `place.name`
- `source` — constant value `google_maps`
- `review_date` — canonical publication timestamp in UTC ISO-8601 or date format
- `rating` — normalized star rating
- `review_text` — free-text review body from `text`
- `owner_response_text` — owner response text if present
- `owner_response_date` — owner response timestamp if present
- `review_url` — safe retained URL if needed for provenance
- `language` — review language when available
- `raw_source_file` — source file name kept only for reproducibility, not as a feature
- `reviewer_id` — only if deduplication or customer-tracking is required; otherwise prefer a de-identified hash or drop it
- `reviewer_name` — optional only if privacy/CRM use case explicitly requires it

The raw exports should remain immutable. The normalization layer should map the branch-specific schemas to this canonical shape before any NLP, mining, or predictive analysis begins.

