// 10 筆生醫與 AI 跨域文獻模擬數據
const PAPERS_MOCK = [
    {
        id: 1,
        title: "CRISPR-Cas9 Gene Editing Efficiency in Human Cells",
        authors: "Jennifer A. Doudna, Emmanuel Charpentier",
        publishDate: "2023-05-12",
        journal: "Nature Biotechnology",
        summary: "This study evaluates the targeting efficiency and off-target effects of CRISPR-Cas9 system across various human primary cell lines.",
        relevanceScore: 95,
        tags: ["CRISPR", "Gene Editing"],
        url: "https://www.nature.com/nbt"
    },
    {
        id: 2,
        title: "Deep Learning for Automated Cancer Histopathology Classification",
        authors: "Andrew Ng, Fei-Fei Li",
        publishDate: "2024-01-15",
        journal: "IEEE Transactions on Medical Imaging",
        summary: "An end-to-end convolutional neural network (CNN) designed to classify breast cancer histopathological images with expert-level accuracy.",
        relevanceScore: 90,
        tags: ["AI", "Cancer", "Deep Learning"],
        url: "https://ieeexplore.ieee.org"
    },
    {
        id: 3,
        title: "Single-Cell RNA-Seq Reveals Immune Microenvironment in Lung Cancer",
        authors: "Sarah Teichmann",
        publishDate: "2022-11-30",
        journal: "Cell",
        summary: "Profiling over 50,000 single cells to map the cellular landscape and immune suppression mechanisms in non-small cell lung cancer.",
        relevanceScore: 85,
        tags: ["Single-Cell", "Bioinformatics", "Cancer"],
        url: "https://www.cell.com"
    },
    {
        id: 4,
        title: "mRNA Vaccine Delivery Systems: Lipid Nanoparticles Optimization",
        authors: "Robert Langer, Katalin Karikó",
        publishDate: "2023-08-22",
        journal: "Advanced Materials",
        summary: "Systematic screening of novel ionizable lipids to enhance the delivery and translation of mRNA vaccines in vivo.",
        relevanceScore: 88,
        tags: ["mRNA", "Vaccine"],
        url: "https://onlinelibrary.wiley.com"
    },
    {
        id: 5,
        title: "Machine Learning in Virtual Screening for Drug Discovery",
        authors: "Demis Hassabis",
        publishDate: "2024-03-05",
        journal: "Journal of Medicinal Chemistry",
        summary: "Integrating deep generative models to speed up the identification of high-affinity small molecule inhibitors for target proteins.",
        relevanceScore: 92,
        tags: ["AI", "Drug Discovery"],
        url: "https://pubs.acs.org"
    },
    {
        id: 6,
        title: "Clinical Efficacy of CAR-T Cell Therapy in B-Cell Lymphoma",
        authors: "Carl June",
        publishDate: "2021-06-18",
        journal: "New England Journal of Medicine",
        summary: "Long-term follow-up results demonstrating durable complete responses in patients with refractory large B-cell lymphoma treated with CAR-T.",
        relevanceScore: 78,
        tags: ["CAR-T", "Cancer"],
        url: "https://www.nejm.org"
    },
    {
        id: 7,
        title: "AlphaFold 3: Predicting Biomolecular Structures and Interactions",
        authors: "John Jumper, Demis Hassabis",
        publishDate: "2024-05-10",
        journal: "Nature",
        summary: "Introducing AlphaFold 3, which predicts the 3D structures and chemical modifications of proteins, DNA, RNA, and chemical complexes.",
        relevanceScore: 98,
        tags: ["AI", "AlphaFold", "Protein Structure"],
        url: "https://www.nature.com"
    },
    {
        id: 8,
        title: "Applications of CRISPR in Agricultural Genetic Engineering",
        authors: "Feng Zhang",
        publishDate: "2022-04-02",
        journal: "Plant Physiology",
        summary: "Reviewing how CRISPR technology is utilized to create disease-resistant, drought-tolerant crop varieties to tackle global food security.",
        relevanceScore: 80,
        tags: ["CRISPR", "Agriculture"],
        url: "https://academic.oup.com/plphys"
    },
    {
        id: 9,
        title: "AI-Driven Interpretation of Electrocardiograms in Emergency Care",
        authors: "Eric Topol",
        publishDate: "2023-10-14",
        journal: "The Lancet",
        summary: "A randomized controlled trial testing an AI algorithm's ability to alert clinicians to acute myocardial infarction in real-time.",
        relevanceScore: 72,
        tags: ["AI", "Clinical Medicine"],
        url: "https://www.thelancet.com"
    },
    {
        id: 10,
        title: "The Landscape of Somatic Mutations in Human Cancers",
        authors: "Mike Stratton",
        publishDate: "2020-02-05",
        journal: "Nature Genetics",
        summary: "A comprehensive analysis of cancer genomes across 38 tumor types, identifying novel driver mutations and mutational signatures.",
        relevanceScore: 65,
        tags: ["Cancer", "Genomics"],
        url: "https://www.nature.com/ng"
    }
];

// ==================== 狀態管理 (State) ====================
let currentKeyword = ""; // 儲存使用者輸入的關鍵字
let selectedTag = null;  // 儲存目前選取的單一標籤（null 代表未選取，顯示全部）

// ==================== 渲染與處理邏輯 (IPO) ====================

// 1. 動態生成不重複的標籤按鈕
function renderTagButtons() {
    const tagsContainer = document.getElementById("tags-filter-container");
    
    // 提取所有論文中出現過的標籤，並利用 Set 去除重複
    const allTags = new Set();
    PAPERS_MOCK.forEach(paper => {
        paper.tags.forEach(tag => allTags.add(tag));
    });

    // 生成「全部清除」按鈕 + 各個標籤按鈕
    let tagsHtml = `<button class="tag-btn ${selectedTag === null ? 'active' : ''}" onclick="selectTag(null)">顯示全部</button>`;
    
    allTags.forEach(tag => {
        const isActive = selectedTag === tag ? 'active' : '';
        tagsHtml += `<button class="tag-btn ${isActive}" onclick="selectTag('${tag}')">${tag}</button>`;
    });

    tagsContainer.innerHTML = tagsHtml;
}

// 2. 切換選取標籤的行為
function selectTag(tag) {
    selectedTag = tag;
    renderTagButtons(); // 重新渲染按鈕狀態
    filterAndRender();  // 執行篩選
}

// 3. 核心過濾與渲染控制
function filterAndRender() {
    // Input：從 PAPERS_MOCK 開始篩選
    let filtered = PAPERS_MOCK;

    // Process A：關鍵字篩選（不分大小寫，同時比對標題、作者與摘要）
    if (currentKeyword.trim() !== "") {
        const query = currentKeyword.toLowerCase().trim();
        filtered = filtered.filter(paper => {
            return paper.title.toLowerCase().includes(query) || 
                   paper.authors.toLowerCase().includes(query) || 
                   paper.summary.toLowerCase().includes(query);
        });
    }

    // Process B：標籤篩選
    if (selectedTag !== null) {
        filtered = filtered.filter(paper => paper.tags.includes(selectedTag));
    }

    // Output：將最後篩選結果渲染到畫面上
    renderPapers(filtered);
}

// 4. 基礎論文渲染（支援無結果顯示）
function renderPapers(papersArray) {
    const container = document.getElementById("papers-container");
    
    if (papersArray.length === 0) {
        container.innerHTML = `<p style="color: #999; text-align: center; padding: 40px;">找不到符合 "${currentKeyword}" 且標籤為 "${selectedTag || '全部'}" 的結果</p>`;
        return;
    }

    let htmlContent = "";
    papersArray.forEach(paper => {
        const tagsHtml = paper.tags.map(tag => `<span class="tag">${tag}</span>`).join("");

        htmlContent += `
            <div class="paper-card">
                <h3 class="paper-title">
                    <a href="${paper.url}" target="_blank">${paper.title}</a>
                </h3>
                <div class="meta-info">
                    作者: ${paper.authors} | 
                    出版日期: ${paper.publishDate} | 
                    期刊: <em>${paper.journal}</em> | 
                    相關度評分: <span class="score">${paper.relevanceScore}%</span>
                </div>
                <p class="summary">${paper.summary}</p>
                <div class="tags">${tagsHtml}</div>
            </div>
        `;
    });

    container.innerHTML = htmlContent;
}

// ==================== 事件監聽註冊 ====================
document.addEventListener("DOMContentLoaded", () => {
    // 初始化畫面
    renderTagButtons();
    filterAndRender();

    // 監聽搜尋按鈕點擊事件（驗收條件 1）
    document.getElementById("search-btn").addEventListener("click", () => {
        currentKeyword = document.getElementById("search-input").value;
        filterAndRender();
    });

    // 監聽輸入框的 Enter 鍵事件（優化操作體驗）
    document.getElementById("search-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            currentKeyword = document.getElementById("search-input").value;
            filterAndRender();
        }
    });
});