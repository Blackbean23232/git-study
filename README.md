# git-study

Git의 기본 사용법을 정리한 학습용 저장소입니다.

## 목차

1. [Git이란?](#git이란)
2. [설치 및 초기 설정](#설치-및-초기-설정)
3. [기본 작업 흐름](#기본-작업-흐름)
4. [자주 쓰는 명령어](#자주-쓰는-명령어)
5. [브랜치](#브랜치)
6. [원격 저장소](#원격-저장소)
7. [되돌리기](#되돌리기)
8. [충돌 해결](#충돌-해결)
9. [커밋 메시지 작성 팁](#커밋-메시지-작성-팁)
10. [.gitignore](#gitignore)

## Git이란?

Git은 파일의 변경 이력을 기록하고 관리하는 **분산 버전 관리 시스템**입니다.

- 언제, 누가, 무엇을 바꿨는지 추적할 수 있습니다.
- 이전 상태로 되돌릴 수 있습니다.
- 여러 사람이 같은 프로젝트에서 동시에 작업할 수 있습니다.

> Git은 도구이고, GitHub는 Git 저장소를 온라인에 올려 공유하는 서비스입니다.

### 3가지 영역

```
작업 디렉토리  --git add-->  스테이징 영역  --git commit-->  로컬 저장소  --git push-->  원격 저장소
(Working Dir)                (Staging Area)                (Repository)                (GitHub 등)
```

## 설치 및 초기 설정

설치 확인:

```bash
git --version
```

처음 한 번만 사용자 정보를 등록합니다. 이 정보는 커밋에 기록됩니다.

```bash
git config --global user.name "이름"
git config --global user.email "email@example.com"
```

설정 확인:

```bash
git config --list
```

## 기본 작업 흐름

### 1. 저장소 만들기

새 저장소 생성:

```bash
git init
```

기존 원격 저장소 복제:

```bash
git clone <저장소 URL>
```

### 2. 변경 → 스테이징 → 커밋

```bash
git status                  # 현재 상태 확인
git add 파일명              # 특정 파일 스테이징
git add .                   # 모든 변경 사항 스테이징
git commit -m "커밋 메시지" # 커밋 생성
```

### 3. 원격 저장소에 올리기

```bash
git push origin main
```

### 4. 원격 저장소의 변경 가져오기

```bash
git pull origin main
```

## 자주 쓰는 명령어

| 명령어 | 설명 |
| --- | --- |
| `git init` | 현재 폴더를 Git 저장소로 초기화 |
| `git clone <URL>` | 원격 저장소 복제 |
| `git status` | 변경된 파일 상태 확인 |
| `git add <파일>` | 변경 사항을 스테이징 영역에 추가 |
| `git commit -m "<메시지>"` | 스테이징된 변경 사항을 커밋 |
| `git log` | 커밋 이력 조회 |
| `git log --oneline --graph` | 커밋 이력을 한 줄·그래프로 조회 |
| `git diff` | 작업 디렉토리의 변경 내용 확인 |
| `git diff --staged` | 스테이징된 변경 내용 확인 |
| `git branch` | 브랜치 목록 확인 |
| `git switch <브랜치>` | 브랜치 이동 |
| `git merge <브랜치>` | 브랜치 병합 |
| `git fetch` | 원격 변경 사항 확인(병합 X) |
| `git pull` | 원격 변경 사항 가져와 병합 |
| `git push` | 로컬 커밋을 원격에 업로드 |

## 브랜치

브랜치는 독립적으로 작업할 수 있는 갈래입니다. 기능 개발이나 버그 수정은 `main`이 아닌 별도 브랜치에서 하는 것이 좋습니다.

```bash
git branch                    # 브랜치 목록
git branch feature/login      # 브랜치 생성
git switch feature/login      # 브랜치 이동
git switch -c feature/login   # 생성과 이동을 한 번에
git branch -d feature/login   # 병합된 브랜치 삭제
```

### 브랜치 병합

```bash
git switch main
git merge feature/login
```

### 일반적인 브랜치 작업 흐름

```bash
git switch -c feature/login   # 1. 작업용 브랜치 생성
# ... 코드 수정 ...
git add .                     # 2. 스테이징
git commit -m "로그인 기능 추가" # 3. 커밋
git push -u origin feature/login # 4. 원격에 업로드
# 5. GitHub에서 Pull Request 생성 → 리뷰 → main에 병합
```

## 원격 저장소

```bash
git remote -v                                  # 연결된 원격 저장소 확인
git remote add origin <저장소 URL>             # 원격 저장소 연결
git push -u origin main                        # 최초 push (upstream 설정)
git fetch origin                               # 원격 변경 사항 가져오기(병합 X)
git pull origin main                           # 가져오기 + 병합
```

## 되돌리기

| 상황 | 명령어 |
| --- | --- |
| 작업 디렉토리의 변경을 취소 | `git restore <파일>` |
| 스테이징 취소 (`git add` 되돌리기) | `git restore --staged <파일>` |
| 마지막 커밋 메시지 수정 | `git commit --amend` |
| 커밋을 취소하고 변경은 유지 | `git reset --soft HEAD~1` |
| 커밋을 취소하고 변경은 스테이징 해제 | `git reset HEAD~1` |
| 커밋과 변경을 모두 삭제 | `git reset --hard HEAD~1` |
| 이력은 남기고 커밋을 취소하는 새 커밋 생성 | `git revert <커밋 해시>` |

> ⚠️ `git reset --hard`와 `git restore <파일>`은 저장하지 않은 변경 사항을 **영구 삭제**합니다. 이미 push한 커밋은 `reset` 대신 `revert`를 사용하세요.

## 충돌 해결

같은 파일의 같은 부분을 서로 다르게 수정하면 병합 시 충돌(conflict)이 발생합니다.

1. `git status`로 충돌 파일 확인
2. 파일을 열어 충돌 표시를 직접 수정

   ```
   <<<<<<< HEAD
   현재 브랜치의 내용
   =======
   병합하려는 브랜치의 내용
   >>>>>>> feature/login
   ```

3. 마커(`<<<<<<<`, `=======`, `>>>>>>>`)를 지우고 최종 내용만 남김
4. 해결한 파일을 스테이징하고 커밋

   ```bash
   git add 파일명
   git commit
   ```

병합을 취소하려면:

```bash
git merge --abort
```

## 커밋 메시지 작성 팁

- 무엇을, 왜 바꿨는지 간결하게 작성합니다.
- 하나의 커밋에는 하나의 목적만 담습니다.
- 자주 쓰는 접두어 예시:

| 접두어 | 의미 |
| --- | --- |
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `style` | 코드 포맷팅 (동작 변화 없음) |
| `refactor` | 리팩토링 |
| `test` | 테스트 코드 추가/수정 |
| `chore` | 빌드, 설정 등 기타 작업 |

예시:

```
feat: 로그인 기능 추가
fix: 회원가입 시 이메일 중복 검사 오류 수정
docs: README에 Git 사용법 추가
```

## .gitignore

Git이 추적하지 않을 파일/폴더를 지정하는 파일입니다. 저장소 최상위에 `.gitignore` 파일을 만들어 작성합니다.

```gitignore
# 의존성
node_modules/

# 환경 변수 / 비밀 정보
.env

# 빌드 결과물
dist/
build/

# 로그 및 OS 파일
*.log
.DS_Store
Thumbs.db
```

> 이미 커밋된 파일은 `.gitignore`에 추가해도 계속 추적됩니다. 추적을 해제하려면 `git rm --cached <파일>`을 사용하세요.
