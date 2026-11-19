# KẾ HOẠCH ĐỒ ÁN: HỆ THỐNG LUYỆN NGHE CHÉP CHÍNH TẢ (DICTATION)

> Nhóm 5 người, đồ án cuối kỳ. Yêu cầu: áp dụng **Architecture Pattern** và **Design Pattern**.
> Stack đề xuất (có thể đổi): **FastAPI (Python) + Celery/Redis + PostgreSQL + React + Docker Compose**.
> Lý do chọn Python: Whisper, yt-dlp, FFmpeg wrapper đều có hệ sinh thái Python mạnh nhất.

---

## 1. Tổng quan

### 1.1 Bài toán
Xây dựng ứng dụng web hỗ trợ học tiếng Anh bằng phương pháp nghe chép chính tả. Người dùng cung cấp đường dẫn YouTube hoặc upload file âm thanh. Hệ thống tự động:
1. Lấy media và trích xuất âm thanh.
2. Lấy phụ đề có sẵn hoặc nhận dạng giọng nói (Speech-to-Text).
3. Phân tách câu và đồng bộ timestamp.
4. Tạo bài luyện tập tương tác có chấm điểm.

### 1.2 Mục tiêu kiến trúc (trọng tâm chấm điểm)

| Mục tiêu | Ý nghĩa | Cách chứng minh khi demo |
|---|---|---|
| **Extensibility** | Thêm nguồn dữ liệu / thuật toán chấm mới mà không sửa code lõi (Open/Closed) | Thêm `PodcastSource` hoặc `WerScoring` chỉ bằng một class mới |
| **Asynchronous / Non-blocking** | Tác vụ nặng chạy nền, không nghẽn luồng chính | Xử lý video dài, UI vẫn dùng được, thanh tiến độ realtime |
| **Decoupling** | Logic nghiệp vụ tách khỏi thư viện bên thứ ba | Thay Whisper bằng mock/engine khác mà core không đổi |

### 1.3 Phạm vi (Scope)

**Trong phạm vi (In scope):** Auth, ingestion (YouTube/file), pipeline nền, player luyện tập, chấm điểm, tiến độ/thống kê, quản trị cơ bản.

**Ngoài phạm vi (Out of scope):** Mobile app, thanh toán, microservices đầy đủ, huấn luyện model AI riêng.

### 1.4 Rủi ro và cách xử lý

| Rủi ro | Mức | Giải pháp |
|---|---|---|
| Tải video YouTube vi phạm điều khoản và hay bị chặn | Cao | Ưu tiên lấy **caption có sẵn**; upload file là nguồn chính; ghi rõ mục đích học thuật trong báo cáo |
| Whisper chậm, thiếu GPU | Cao | Dùng `faster-whisper` model `base/small` trên CPU; giới hạn độ dài media; job queue |
| Timestamp lệch | Trung bình | Dùng word-level timestamp, gom thành câu theo dấu câu và khoảng lặng |
| Video quá dài làm nghẽn | Trung bình | Giới hạn thời lượng (ví dụ ≤ 15 phút), hàng đợi, hiển thị tiến độ |
| Tích hợp muộn gây lỗi dồn cuối kỳ | Cao | Chốt API contract tuần 1, tích hợp liên tục mỗi tuần |
| Phụ thuộc nhau giữa các thành viên | Trung bình | Dùng mock adapter/fake data để làm song song |

---

## 2. Kiến trúc hệ thống

### 2.1 Architecture Pattern

**Hexagonal Architecture (Ports & Adapters) + Event-driven / Job Queue**

```
┌────────────────┐   REST / WebSocket(SSE)   ┌──────────────────────────┐
│ React Frontend │ <───────────────────────> │ API Layer (FastAPI)      │
└────────────────┘                           │  Controller / Facade     │
                                             └─────────────┬────────────┘
                                                           │ Application Services (Use cases)
                                             ┌─────────────▼────────────┐
                                             │ DOMAIN CORE              │
                                             │ Lesson, Sentence,        │
                                             │ Attempt, Job, Scoring    │
                                             │ (không biết thư viện ngoài)
                                             └───┬──────────┬───────────┘
                                   Ports (interface)        │
                  ┌──────────────┬───────────────┼──────────┴────────┐
                  ▼              ▼               ▼                   ▼
          MediaSourcePort  TranscriberPort  AudioProcessorPort  RepositoryPort
          (YouTube/File/   (Whisper/Mock)   (FFmpeg)            (PostgreSQL)
           Podcast...)
                                   │
                         publish job│
                           ┌────────▼────────┐
                           │ Queue (Redis)   │
                           └────────┬────────┘
                           ┌────────▼───────────────────────────────┐
                           │ Worker (Celery): Processing Pipeline    │
                           │ Fetch → Extract audio → Transcribe →    │
                           │ Segment → Sync timestamp → Save         │
                           └─────────────────────────────────────────┘
```

**Nguyên tắc:**
- Dependency hướng vào trong: Domain không import YouTube/FFmpeg/Whisper.
- Mọi thư viện ngoài chỉ xuất hiện trong lớp **Adapter**.
- Tác vụ nặng chạy ở **Worker**, API chỉ nhận request và trả `job_id`.

### 2.2 Cấu trúc thư mục đề xuất

```
dictation-app/
├── backend/
│   ├── app/
│   │   ├── api/                 # Controllers, schemas (DTO), dependencies
│   │   ├── application/         # Use cases, Facade, Command
│   │   ├── domain/              # Entities, value objects, ports (interfaces), events
│   │   │   ├── models/
│   │   │   ├── ports/           # MediaSourcePort, TranscriberPort, ScoringStrategy...
│   │   │   └── services/        # Scoring, segmentation (logic thuần)
│   │   ├── infrastructure/
│   │   │   ├── adapters/        # YtDlpAdapter, FFmpegAdapter, WhisperAdapter
│   │   │   ├── persistence/     # Repository implementations, ORM
│   │   │   ├── queue/           # Celery tasks, publisher
│   │   │   └── cache/
│   │   └── worker/              # Pipeline, handlers
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   └── src/ (components, pages, hooks, services, store)
├── docs/                        # UML, ERD, API spec, báo cáo
├── docker-compose.yml
└── README.md
```

---

## 3. Design Pattern và vị trí áp dụng

Tổng cộng **15 vị trí áp dụng (14 pattern khác nhau, State dùng 2 lần)**, chia đều **mỗi người 3 pattern** (xem cột "Người phụ trách").

| # | Pattern | Áp dụng | Mục tiêu | Người phụ trách |
|---|---|---|---|---|
| 1 | **Repository** | Truy cập dữ liệu qua interface (`LessonRepository`, `AttemptRepository`...) | Decoupling | **A** |
| 2 | **Singleton** | Config, connection pool, queue client (qua dependency injection) | Quản lý tài nguyên | **A** |
| 3 | **Decorator** | Cache transcript theo hash media, logging, đo thời gian quanh service | Hiệu năng | **A** |
| 4 | **Factory** | `MediaSourceFactory` tạo `YouTubeSource`, `LocalFileSource`, `PodcastSource` | Extensibility | **B** |
| 5 | **Adapter** | `YtDlpAdapter`, `FFmpegAdapter` cài đặt Port, `CaptionAdapter` lấy phụ đề có sẵn | Decoupling | **B** |
| 6 | **Template Method** | Khung ingest: validate → fetch → extract audio; mỗi nguồn override bước `fetch` | Extensibility | **B** |
| 7 | **Command** | `ProcessMediaCommand` đóng gói job đưa vào queue (hủy, retry) | Async | **C** |
| 8 | **State** (Job) | Trạng thái job: Pending → Downloading → Transcribing → Segmenting → Done / Failed | Async | **C** |
| 9 | **Chain of Responsibility / Pipeline** | Chuỗi bước xử lý: làm sạch text, lọc nhạc nền, tách câu, đồng bộ timestamp. Kèm `WhisperAdapter` | Extensibility | **C** |
| 10 | **Strategy** | `ScoringStrategy`: ExactMatch, Levenshtein, WER, WordByWord | Extensibility | **D** |
| 11 | **Facade** | `PracticeFacade`, `LessonFacade` gom nhiều service cho controller | Gọn code | **D** |
| 12 | **Builder** | Dựng `FeedbackReport` (diff từng từ, điểm, gợi ý) và bộ lọc thống kê | Dễ đọc, linh hoạt | **D** |
| 13 | **Observer** | Frontend đăng ký nhận event tiến độ job qua SSE/WebSocket; store cập nhật UI khi dữ liệu đổi | Async | **E** |
| 14 | **State** (Player) | Máy trạng thái của player: Idle → PlayingSentence → WaitingInput → Reviewing → Finished | Dễ bảo trì UI | **E** |
| 15 | **Proxy** | `ApiClient` bọc `fetch`: tự gắn token, refresh token khi hết hạn, cache GET, xử lý lỗi chung | Decoupling | **E** |

> Lưu ý: chọn dùng **đúng chỗ**, mỗi pattern cần có (1) sơ đồ lớp, (2) lý do dùng, (3) code ví dụ. Nếu thiếu thời gian, ưu tiên các pattern **4, 5, 7, 8, 10, 13** làm điểm nhấn demo.
> Pattern **State** xuất hiện ở hai ngữ cảnh khác nhau (Job ở backend của C, Player ở frontend của E), nên trong báo cáo hãy trình bày thành hai ví dụ riêng.

---

## 4. Danh sách module và chức năng

### M1. Auth và người dùng
- Đăng ký, đăng nhập (JWT), refresh token, đổi mật khẩu.
- Phân quyền: User, Admin.
- Cài đặt cá nhân: tốc độ phát mặc định, độ khó, ngôn ngữ giao diện.

### M2. Media Ingestion
- Nhập URL YouTube / upload file (mp3, wav, mp4, m4a).
- Kiểm tra hợp lệ (định dạng, kích thước, thời lượng).
- Lấy caption có sẵn nếu có; nếu không thì chuyển sang STT.
- Chống trùng: băm media, dùng lại kết quả đã xử lý.

### M3. Processing Pipeline (nền)
- Tạo job, đưa vào queue, worker xử lý.
- FFmpeg: tách audio, chuẩn hóa (16kHz mono).
- Whisper: transcribe với word-level timestamp.
- Tách câu và đồng bộ timestamp.
- Theo dõi tiến độ, retry khi lỗi, hủy job.

### M4. Bài luyện tập (Practice Player)
- Phát từng câu theo timestamp.
- Lặp câu, làm chậm (0.5x–1.5x), tua nhanh câu trước/sau.
- Ô nhập chính tả, gợi ý (hiện từ đầu, số từ), bỏ qua câu.
- Chế độ: chép toàn câu / điền từ thiếu (cloze).

### M5. Chấm điểm và phản hồi
- So sánh theo từng từ, tô màu đúng / sai / thiếu / thừa.
- Chuẩn hóa trước khi chấm (hoa thường, dấu câu, viết tắt).
- Chọn thuật toán chấm (Strategy), tính điểm theo câu và theo bài.

### M6. Tiến độ và thống kê
- Lịch sử luyện tập, điểm theo thời gian, streak.
- Thống kê từ hay sai, loại lỗi thường gặp.
- Dashboard cá nhân.

### M7. Quản lý bài học và quản trị
- Thư viện bài học (của tôi / công khai), gắn thẻ, cấp độ.
- Admin: quản lý user, duyệt bài học công khai, xem trạng thái job, log hệ thống.

### M8. Nâng cao (làm nếu còn thời gian)
- Podcast / RSS source (chứng minh extensibility).
- Sổ từ vựng từ các từ hay sai, ôn tập lặp lại ngắt quãng.
- Xuất báo cáo PDF/Excel.

---

## 5. Phân công công việc

| Thành viên | Vai trò | Module chính | Pattern chính (3 mỗi người) | Trách nhiệm chung |
|---|---|---|---|---|
| **A** | Trưởng nhóm, Backend lead | M1, M7 (backend), khung hệ thống, Docker, CI | Repository, Singleton, Decorator | Dựng skeleton, review PR, tích hợp, quản lý tiến độ |
| **B** | Backend - Ingestion | M2 | Factory, Adapter, Template Method | Adapter YouTube/FFmpeg/caption, tài liệu nguồn media |
| **C** | Backend - Pipeline | M3 | Command, State (Job), Chain of Responsibility | Queue/worker, Whisper, theo dõi job, test pipeline |
| **D** | Backend - Practice/Scoring | M5, M6 | Strategy, Facade, Builder | Thuật toán chấm, feedback, thống kê, unit test scoring |
| **E** | Frontend lead | M4 + giao diện toàn hệ thống, M7 (UI) | Observer, State (Player), Proxy | UI/UX, player, realtime tiến độ, dashboard, API client |

### Chi tiết phần pattern của E (frontend)

| Pattern | Triển khai cụ thể | Sản phẩm kèm theo |
|---|---|---|
| **Observer** | `useJobProgress(jobId)` dùng `EventSource` nhận event tiến độ; store (Zustand/Redux) cho component đăng ký nhận thay đổi | Thanh tiến độ realtime, thông báo khi job xong |
| **State** (Player) | `PlayerStateMachine` với các trạng thái Idle, PlayingSentence, WaitingInput, Reviewing, Finished; mỗi trạng thái quyết định nút nào được bật | Sơ đồ state của player, unit test chuyển trạng thái |
| **Proxy** | `ApiClient` bọc `fetch/axios`: gắn JWT, tự refresh khi 401, cache GET, retry, thông báo lỗi thống nhất | Một nơi duy nhất gọi API, các component không gọi `fetch` trực tiếp |

### Khối lượng công việc E (để cân bằng với backend)
- Phần pattern 3 cái như mọi người, cộng thêm toàn bộ giao diện (đây là khối lượng lớn nên các thành viên backend hỗ trợ):
  - **B** làm giúp trang tạo bài học (form nhập URL/upload, kiểm tra hợp lệ).
  - **D** làm giúp màn hình kết quả chấm điểm (tô màu từng từ) và dashboard thống kê.
  - **A** làm giúp trang login/đăng ký và trang admin.

### Quy ước phối hợp
- **Contract-first:** chốt OpenAPI (Swagger) trong tuần 1; E làm frontend bằng mock server cho tới khi backend sẵn sàng.
- **Mock adapter:** C và D dùng `FakeTranscriber`, `FakeMediaSource` để làm song song khi chưa có Whisper/YouTube thật.
- Mỗi người **tự viết test và tài liệu** cho phần của mình, gồm sơ đồ lớp và giải thích lý do dùng 3 pattern được giao.
- Họp ngắn **2 lần/tuần** (đầu tuần chia việc, cuối tuần demo và tích hợp).

---

## 6. Lộ trình 12 tuần

| Tuần | Giai đoạn | Công việc | Kết quả (Deliverable) |
|---|---|---|---|
| **1** | Phân tích | Chốt phạm vi, use case, rủi ro; chọn stack; tạo repo, quy ước Git | Tài liệu yêu cầu, use case diagram |
| **2** | Thiết kế | ERD, class diagram (đánh dấu pattern), component diagram, OpenAPI contract; dựng skeleton + Docker Compose | Bộ tài liệu thiết kế, repo chạy được `docker compose up` |
| **3** | Nền tảng | A: Auth + khung. B: MediaSource interface + LocalFile. C: Queue + worker "hello world". D: Scoring interface + ExactMatch. E: layout + login | Đăng nhập chạy được, job demo chạy nền |
| **4** | Nền tảng | B: YouTube adapter + FFmpeg. C: Whisper adapter + state job. D: Levenshtein/WER. E: trang tạo bài học | Upload file → có audio, chạy được transcribe |
| **5** | Tính năng | Pipeline đầy đủ (fetch → transcribe → segment). Player cơ bản | **Milestone 1:** luồng "upload → ra câu có timestamp" |
| **6** | Tính năng | SSE/WebSocket tiến độ; practice API; UI chép chính tả + chấm điểm | **Milestone 2:** làm được 1 bài luyện hoàn chỉnh |
| **7** | Tính năng | Thống kê, lịch sử, thư viện bài học, cloze mode | Dashboard cơ bản |
| **8** | Tính năng | Admin, cache transcript, retry/cancel job, xử lý lỗi | **Milestone 3:** đủ tính năng chính (feature freeze) |
| **9** | Tích hợp | Ghép end-to-end, sửa lỗi, tối ưu hiệu năng | Hệ thống chạy trọn vẹn |
| **10** | Mở rộng và test | Thêm Podcast source + thuật toán chấm mới (chứng minh Open/Closed); unit + integration test | Báo cáo coverage, demo extensibility |
| **11** | Hoàn thiện | UI polish, dữ liệu mẫu, tài liệu, sơ đồ cuối | Báo cáo nháp, slide nháp |
| **12** | Bảo vệ | Tập demo 2-3 lần, chốt báo cáo, đóng băng code | Báo cáo, slide, mã nguồn, bản demo |

> Nếu thời gian ngắn hơn, ưu tiên theo thứ tự: **M1 → M2 (file upload) → M3 → M4 → M5 → M6**, cắt M7, M8 trước.

---

## 7. Quy trình làm việc

### 7.1 Git
- Nhánh: `main` (ổn định) ← `develop` ← `feature/<module>-<mô tả>`.
- Pull Request bắt buộc, **ít nhất 1 người review**; không commit trực tiếp vào `main`.
- Commit theo chuẩn: `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `refactor: ...`.

### 7.2 Quản lý công việc
- Dùng GitHub Projects hoặc Trello: cột *Backlog → To Do → In Progress → Review → Done*.
- Mỗi task có người phụ trách, deadline, tiêu chí hoàn thành (Definition of Done).

### 7.3 Definition of Done
- [ ] Code chạy, đã merge qua PR có review.
- [ ] Có unit test cho logic nghiệp vụ.
- [ ] Cập nhật API doc / diagram nếu có thay đổi.
- [ ] Không phá luồng end-to-end hiện có.

### 7.4 Kiểm thử

| Loại | Phạm vi | Công cụ |
|---|---|---|
| Unit test | Scoring strategies, segmentation, state transitions, factory | pytest |
| Integration test | API + DB, pipeline với adapter giả | pytest + testcontainers |
| E2E (nhẹ) | Luồng chính trên UI | Playwright / Cypress |
| Test decoupling | Chạy core với `FakeTranscriber`, không cần Whisper | pytest |

---

## 8. Tài liệu cần nộp

1. **Đặc tả yêu cầu:** use case diagram, mô tả use case chính.
2. **Thiết kế:** ERD, component diagram, class diagram (đánh dấu pattern), sequence diagram luồng "dán URL → ra bài tập", state diagram của Job.
3. **Giải thích pattern:** mỗi pattern gồm vấn đề, vì sao chọn, sơ đồ, đoạn code minh họa.
4. **API:** OpenAPI/Swagger.
5. **Hướng dẫn cài đặt và chạy:** README, `docker compose up`.
6. **Báo cáo kiểm thử:** kết quả test, coverage.
7. **Bảng đóng góp từng thành viên** (đối chiếu với lịch sử commit).

---

## 9. Kịch bản demo (10-15 phút)

1. **Giới thiệu bài toán và kiến trúc** (2 phút): sơ đồ Hexagonal + Queue.
2. **Luồng chính** (4 phút): dán link/upload file → xem tiến độ realtime → có bài luyện → chép chính tả → xem điểm tô màu.
3. **Chứng minh Non-blocking** (1 phút): đang xử lý video dài vẫn thao tác được các chức năng khác.
4. **Chứng minh Extensibility** (3 phút): thêm một `ScoringStrategy` / `MediaSource` mới ngay trên màn hình bằng 1 class, không sửa code cũ.
5. **Chứng minh Decoupling** (2 phút): chạy test với `FakeTranscriber` pass mà không cần Whisper.
6. **Thống kê và quản trị** (1 phút).
7. **Hỏi đáp:** chuẩn bị sẵn câu trả lời cho "Vì sao dùng pattern này ở đây?".

> Chuẩn bị sẵn **dữ liệu mẫu** và **video/audio đã xử lý trước** phòng khi mạng hoặc Whisper chậm lúc demo.

---

## 10. Tiêu chí hoàn thành (Checklist tự đánh giá)

### Kiến trúc và pattern
- [ ] Domain core không import thư viện bên thứ ba.
- [ ] Có ít nhất 6-8 pattern dùng đúng chỗ, mỗi pattern có giải thích.
- [ ] Thêm được nguồn media / thuật toán chấm mới mà không sửa code cũ.
- [ ] Tác vụ nặng chạy nền, API trả về ngay `job_id`.
- [ ] Tiến độ job hiển thị realtime.

### Chức năng
- [ ] Upload file và URL YouTube đều tạo được bài luyện.
- [ ] Phát từng câu, lặp, chậm lại hoạt động.
- [ ] Chấm điểm và tô màu từng từ chính xác.
- [ ] Thống kê tiến độ hiển thị đúng.

### Chất lượng
- [ ] `docker compose up` chạy được toàn hệ thống.
- [ ] Unit test cho scoring, state, factory, segmentation.
- [ ] Lịch sử Git cho thấy mọi thành viên đều đóng góp.
- [ ] Báo cáo và slide hoàn chỉnh, đã tập demo.

---

## 11. Phụ lục: Interface mẫu (tham khảo)

```python
# domain/ports/media_source.py
from abc import ABC, abstractmethod

class MediaSource(ABC):
    @abstractmethod
    def validate(self, ref: str) -> None: ...
    @abstractmethod
    def fetch(self, ref: str) -> "MediaFile": ...

# domain/ports/transcriber.py
class TranscriberPort(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "en") -> "Transcript": ...

# domain/ports/scoring.py
class ScoringStrategy(ABC):
    @abstractmethod
    def score(self, expected: str, actual: str) -> "ScoreResult": ...

# application/factory.py
class MediaSourceFactory:
    _registry: dict[str, type[MediaSource]] = {}

    @classmethod
    def register(cls, kind: str, impl: type[MediaSource]) -> None:
        cls._registry[kind] = impl

    @classmethod
    def create(cls, kind: str) -> MediaSource:
        return cls._registry[kind]()
```

Thêm nguồn mới chỉ cần: tạo class kế thừa `MediaSource` và gọi `MediaSourceFactory.register("podcast", PodcastSource)`.

```
Job State:  PENDING → DOWNLOADING → TRANSCRIBING → SEGMENTING → DONE
                 └────────────── FAILED (retry) / CANCELLED ──────────┘
```
