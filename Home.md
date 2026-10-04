---
type: system
---

# Jebi_research

## 목표

### 구조

| 층 | 이름 | 역할 |
| --- | --- | --- |
| 0 | 수집 (Zotero) | 중요하다고 생각한 자료를 모두 모으고, 색칠하고, 메모한다. 글에 쓰든 안 쓰든 일단 보관한다. |
| 1 | 자료 노트 (`References/`) | 자료 하나에 노트 하나. 내 하이라이트와 메모, 출처 정보가 담긴다. 원문은 고치지 않는다. |
| 2 | 위키 (`Wiki/`) | 주제별로 쌓이는 지식. 여러 자료를 압축하고 연결하며, 같은 주장, 상충하는 주장, 인과 관계, 시간에 따른 변화를 출처와 함께 보여준다. |
| 2.5 | 작업 노트 (`Writing/Drafts/`) | 글 하나를 위한 작업대. 쓴 ref, 연결한 이유, 주저리 생각, 버린 근거, 개요를 모은다. 내가 직접 만든 연결이 담기는 곳이다. |
| 3 | 결과물 (`Writing/Published/`) | 실제 발행한 글. 발행 후에는 고정한다. |

### 흐름

```
Zotero → References ──→ Drafts (내가 연결) → Published
              │              │
              └──→ Wiki ←────┘ (다음 글에도 쓸 연결을 올림)
                    │
                    └──→ 다음 Drafts의 출발점
```

### 원칙

- **위키는 미리 만들지 않고 draft에서 자란다.** 여러 글에 반복되거나 자료가 쌓인 주제만 페이지가 된다.

## 폴더 구조

```
Jebi_research/
├── Home.md              목표와 사용 도구
├── AGENTS.md            AI 작업 규칙 (CLAUDE.md가 불러옴)
├── References/
│   └── Zotero/          ZotLit이 만드는 자료 노트
├── Wiki/
│   └── Index.md         위키 목록
├── Writing/
│   ├── Drafts/
│   │   └── 2026-10_주제/   글 하나 = 폴더 하나 (형식 자유)
│   └── Published/       발행본
├── Assets/              이미지·차트·원자료
└── System/
    ├── Templates/       Obsidian 템플릿 (Wiki)
    ├── ZotLit/          ZotLit 템플릿 (색상별 하이라이트 분류)
    ├── Library.base     자료·위키·글 목록
    └── ingest-log.md    위키 반영 기록
```

## 하이라이트 색상

| 색 | 의미 |
| --- | --- |
| 노랑 | 핵심 주장 |
| 빨강 | 수치·데이터 (인용 근거) |
| 초록 | 내 글에 쓸 부분 |
| 파랑 | 정의·개념 |
| 보라 | 반론·의문 |
| 주황 | 전망·예측 |

자료 노트에는 색상별 소제목(Key claims, Data & figures, For my writing, Definitions & concepts, Counterpoints & questions, Outlook & forecasts)으로 나뉘어 들어오고, 그 밖의 색은 "Other colors"로 모인다. 하이라이트에 단 메모는 **Note:**로 표시된다.

## 도구

Zotero에서 자료를 모으고 하이라이트·메모를 남긴 뒤, Obsidian 플러그인 **ZotLit**으로 `References/Zotero/`에 자료 노트를 가져온다.

| 도구 | 버전 |
| --- | --- |
| Obsidian | 1.13.7 |
| ZotLit (Obsidian 플러그인) | 2.1.4 |
| ZotLit Companion (Zotero 플러그인) | 2.1.4 |
| Zotero | 10.0.5 |
| Better BibTeX | 9.0.63 |

새 환경에서 다시 세팅하는 방법은 [[System/SETUP|SETUP]]을 참고한다.

<!-- 버전 기록일: 2026-10-04 -->
