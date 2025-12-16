// =======================================
// KakaoMap 리뷰 전체 수집용 Puppeteer 크롤러
// - JSON XHR 가로채기
// - page=1,2,3 자동 순회
// - 리뷰 없을 때 종료
// =======================================

const puppeteer = require("puppeteer");
const fs = require("fs");

async function crawlHospital(placeId) {
    const url = `https://place.map.kakao.com/${placeId}`;
    const browser = await puppeteer.launch({
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"]
    });

    const page = await browser.newPage();
    let collected = [];

    console.log(`\n🩺 병원(place_id=${placeId}) 리뷰 수집 시작…`);

    // XHR 감지
    page.on("response", async (response) => {
        const reqUrl = response.url();

        if (reqUrl.includes("/api/v2/reviews/list.json")) {
            try {
                const json = await response.json();
                if (!json?.list) return;

                json.list.forEach((r) => {
                    collected.push({
                        place_id: placeId,
                        review_id: r.reviewId,
                        rating: r.rating,
                        date: r.date,
                        content: r.comment
                    });
                });
            } catch (e) {}
        }
    });

    // 병원 페이지 접속
    await page.goto(url, { waitUntil: "networkidle2" });

    // 후기 탭 클릭 (실패해도 JSON으로 수집 가능)
    try {
        await page.click("a.link_tab[data-tab='review']");
        await page.waitForTimeout(1500);
    } catch {}

    // ----------------------------
    // 페이지 번호 증가하며 리뷰 수집
    // ----------------------------
    let pageNum = 1;
    let stop = false;

    while (!stop) {
        const reviewApiUrl = `https://place.map.kakao.com/api/v2/reviews/list.json?\
page=${pageNum}&size=10&sort=accuracy&no=0&placeId=${placeId}`;

        try {
            const res = await page.goto(reviewApiUrl, { timeout: 5000 });
            const json = await res.json();

            if (!json?.list || json.list.length === 0) {
                stop = true;
                break;
            }

            console.log(`📄 ${pageNum} 페이지 수집: ${json.list.length}개`);
            pageNum++;

        } catch (e) {
            console.log(`⚠ API 요청 실패 → 재시도`);
        }

        await page.waitForTimeout(400);
    }

    await browser.close();

    console.log(`✔ 총 ${collected.length}개 리뷰 수집 완료`);
    return collected;
}

// 실행 예시 (단일 병원)
async function main() {
    const placeId = "705827517"; // 수집할 병원 ID
    const reviews = await crawlHospital(placeId);

    fs.writeFileSync(
        `reviews_${placeId}.json`,
        JSON.stringify(reviews, null, 2),
        "utf-8"
    );

    console.log(`💾 저장 완료 → reviews_${placeId}.json`);
}

main();
