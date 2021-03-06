# Todo w. drf and vue

## 0. 모델 정의

- Todo
  - id
  - is_completed : Boolean
  - content: Char
  - created_at: DateTime
  - order: Float

## 1. 필요한 api

- `POST /api/v1/todo`
  - request
    - content
  - response
    - status: success / failure 중 한 가지 값
    - error: failure 시 error message 전달
    - todo
      - id
      - isCompleted
      - content (최대 200자)
      - created_at
      - order: 정렬에 쓰일 실수형 수
- `GET /api/v1/todo`
  - request
  - response
    - todos: todo 배열
      - id
      - isCompleted
      - content
      - created_at
      - order: 정렬에 쓰일 실수형 수
- `PATCH /api/v1/todo/:id`
  - request
    - isCompleted
    - content
    - order
  - response
    - status: success / failure
    - error: failure 일 때 error 메세지
    - todo
      - id
      - isCompleted
      - content
      - created_at
      - order
- `DELETE /api/v1/todo/:id`
  - request
  - response
    - status: success / failure

## 2. 기능 명세

- 작업 추가 란에서 할 일 추가
  - POST todo
  - 엔터 치면 추가
  - 공백일 경우 추가 안됨, 공백으로 초기화 포커스 유지 - 흔들리는 애니메이션
  - 작업추가란 바텀 이나 탑 적절한 곳에 고정
- 할 일 리스트 전부 조회해서 나타냄
  - GET todo
  - 리스트에는 완료 여부 아이콘, 완료된 애들은 회색 글씨 + 취소선
- 완료된 작업 표시 / 숨기기 버튼
  - 누르면 아래에 완료됨 영역 생기거나 사라지거나
- 할 일의 동그라미 누르면
  - PATCH isCompleted 수정 요청
  - 띵 소리와 함께 사라지는 애니메이션
- 할 일 리스트 수정
  - 엔터 누르면 수정
  - 값이 비었으면 진동
  - 수정되고 나서 포커스아웃(블러)
  - 엔터 누르지 않고 포커스 아웃 되면 다시 원래 값으로 돌림
- 할일 드래그
  - PATCH 목록 순서 수정 - 수정된 위치의 이전과 이후의 중간으로 order값 수정 요청
- 할일 삭제
  - 컴펌 받는 모달이나 그냥 컨펌창
  - 휴지통 소리나면서 삭제요청

## 3. 개발 일지

### 1. 백엔드

- 아이템의 순서를 db에 기록을 할 때, 어떻게 해야할 까 - order라는 FloatField를 만들고, 초기 값은 id와 같도록 지정했다. 나중에 순서가 조정되면, 이전 아이템의 order와 다음아이템의 order의 중간값을 넣어 업데이트 할 생각.

  - `__init__` 에서 order값 id로 지정해준 것 까진 좋았는데, 처음선언할 때 `*args,**kwargs` 해주는거 깜빡함. `super().__init__()`에서 `init` 에다가 `*args, **kwargs` 넘겨 주는 거도 같이 깜빡함.

    ```sh
    TypeError: __init__() got an unexpected keyword argument 'content'
    ```

  - 왜 model클래스에서 `__init__` 의 `self`에 접근하지 못할까??

  - default가 굳이 id가 아니더라도 그냥 auto increse하기만 하면 되는데, 굳이 그거에 갇혀서 삽질을 오지게 했다. django의 `AutoField` 는 정수형이라 내가 구현하고자 하는 알고리즘에 맞지 않아서, 커스텀 클래스를 만들어서 사용했다. 필드의 `default` 옵션에 콜백을 줄 수 있는 지 처음 알았다.

  - 이러니까 서버를 껐다 켰을 때가 문제다..ㅠㅠ 결국 db를 활용하긴 해야되는데..어떡해야하나 아 커밋폴스로 해결해볼까 - save를 해야 id가 생기는듯  그냥 두번 요청보내는 걸로 합의 - 실제로 쿼리 두번날리는 거겠지?.. 일단 넘어감 되니까

- `serializer` 에 인스턴스 불러와서 지정해줄 때 `many=True` 빼먹어서 헤맴

  ```sh
  AttributeError: Got AttributeError when attempting to get a value for field `content` on serializer `TodoSerializer`.
  The serializer field might be named incorrectly and not match any attribute or key on the `QuerySet` instance.
  Original exception text was: 'QuerySet' object has no attribute 'content'.
  ```

- 처음 시작할 때는 try except로 감싸서 status 구현해줄랬는데, 순서 알고리즘 구현하다가 시간 다잡아먹고 체력도 떨어져서 스킵

### 2. 프론트엔드

- 컴포넌트 구조 짜보자 (대문자는 컴포넌트 이름, 소문자는 data)
  - App
    - todos
    - TodoInput
      - newTodo
    - TodoList
      - toggleDisplayCompleted
      - TodoListItem
- `@blur` : focus out 이벤트
- 수정 완료될 경우 blur이벤트 발생시키기 위해 ref속성 사용
- 완료 여부 수정하다보니까 PATCH로 `isCompleted`만 전송하니까 valid 통과 못함 - content 영역 `blank=True` 옵션 추가해 줬는데, 이렇게 하면 빈 투두를 만들 때 서버 쪽에서 검증이 안된다. 아마 validation 로직을 따로 짜서 활용하는 기능이 있을 것 같은데, 귀찮으므로 패스. PATCH를 할 때 `content`를 넣어서 요청보낼 수도 있는데, 이렇게 하려면 `PUT` 요청이 아마 더 맞을 거다.
- `keydown`으로 한글 치고 엔터 처리하니까 요청 두 번 간다. mac에서만 그런건지는 모르겠는데 `keypress`로 바꾸자
- 투두 순서 드래그해서 바뀔 수 있게 해볼랬는데, 기존에 있던 vuedraggable은 커스터마이징 하려니까 또 사용법을 익히는 느낌이라 일단 배포부터 해놓고, vanillajs로 만들어보기로 생각함

### 3. 알게 된 잡 지식

- mac기준 `ctrl + -` 누르면 이전 커서 위치로 돌아감 개꿀

### 4. 배포하기

#### 1. 백엔드

1. `Debug=False` 만 해주고, 시크릿 키는 그냥 귀찮아서 냅두기로.

2. `Procfile`을 설정해 주었다. gunicorn을 헤로쿠에서 웹서버로 추천한대니까 그것도 같이 설치.

   ```
   web: gunicorn locallibrary.wsgi --log-file -
   ```

3. ```sh
   $ pip install gunicorn
   ```

4. 데이터 베이스 설정, 헤로쿠의 데이터베이스 url 관련 설정을 알아서 해주는 애가 있어서 설치해서 설정해준다.

   ```sh
   $ pip install dj-database-url
   ```

   ```python
   # settings.py
   # Heroku: Update database configuration from $DATABASE_URL.
   import dj_database_url
   db_from_env = dj_database_url.config(conn_max_age=500)
   DATABASES['default'].update(db_from_env)
   ```

5. `psycopg2`가 장고에서 postgresql쓰려면 있어야 하는애인데, 개발환경에서도 똑같이 설정해서 개발하려면 설치할 필요가 있지만, 그게 아니라면 굳이 로컬에서 설치할 필요는 없다. 그냥 `pip install psycopg2`하면 에러가 나기도하고, 여튼 귀찮은일이다. 헤로쿠에만 필요하니까 `requirements.txt`에만 추가해주면 된다. 아래처럼 하면 된다.

   ```
   dj-database-url==0.4.1
   Django==2.0
   gunicorn==19.6.0
   psycopg2==2.6.2 # 다른부분은 예시, 이 부분만 추가하면 됨
   ```

6. 스태틱파일은 나는 없으므로 관련설정은 하지 않았다. (`whitenoise`관련 설정)

7. `runtime.txt` 파일을 만들어서 파이썬 쓸거라고 알려준다.

   ```
   python-3.7.3
   ```

8. 변경사항 저장하고 서버 잘 돌아가는 지 확인 후 커밋한다.

9. 헤로쿠 cli 설치, 나는 mac이니깐 homebrew로ㅎ

   ```sh
   $ brew tap heroku/brew && brew install heroku
   ```

10. 백엔드 루트디렉토리에서 헤로쿠 원격 저장소를 생성

    ```sh
    $ heroku create bingbingba-todo-drf
    ```

11. ```sh
    $ git push heroku master
    ```

12. 에러 만남ㅎ

    ```sh
    To https://git.heroku.com/bingbingba-todo-drf.git
     ! [remote rejected] master -> master (pre-receive hook declined)
    error: 레퍼런스를 'https://git.heroku.com/bingbingba-todo-drf.git'에 푸시하는데 실패했습니다
    ```

    조금 더 위를 봤더니 이런 메세지가 보인다.

    ```sh
    remote:        django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path.
    ```

    나는 스태틱 파일 쓴거 없으니까 설정 안해도 되겠지 했는데 아니었다ㅎ 스태틱 루트는 설정해줘야 배포해준대여

    ```python
    # settings.py
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    ```

    또 에러가 나서 봤더니 requirements.txt 파일이 그냥 아~까 그대로..ㅎㅎ 새로 프리즈 해주고 psycopg2도 넣어준다. 이런거는 확실히 노드가 편한 듯.

    근데 또 실패했다.

    ```sh
    remote:            Error: could not determine PostgreSQL version from '12.3'
    remote:            ----------------------------------------
    remote:        ERROR: Command errored out with exit status 1: python setup.py egg_info Check the logs for full command output.
    remote:  !     Push rejected, failed to compile Python app.
    ```

    postgresql 관련해서 에러가 나는 듯 한데, 혹시 psycopg2 버전이 너무 낮은건가? requirements.txt에 있는 psycopg2의 버전을 그냥 없애버렸다. 일단 배포 성공ㅎ

13. 이제 마이그레이션 하면 된다.

    ```sh
    $ heroku run python manage.py migrate
    ```

14. 마이그레이션하기 전에 접속을 했었는데 에러가 났었는데, 마이그레이션해도 재배포가 되진 않은 것 같다. 다시 배포하기 위해서 아무 변경사항이나 만들어 커밋하자.

    그게 문제가 아니었네, 접속 실패. 에러로그를 보니까 빌드는 성공했는데 gunicorn 으로 앱서버 시작하는 과정에서 실패했다고 뜬다. Procfile이 문제가 있는게 아닐까 해서 이전에 했던 파일을 찾아보았다.

    아 `wsgi` 파일 이름을 아무 생각 없이 복붙 했구나. `프젝이름.wsgi`로 변경하자.

15. 백엔드 배포 최종 성공ㅠㅠ 

16. 나는 settings.py의 `ALLOWED_HOSTS` 를 그냥 `*`로 다 설정해 줬는데, 필요하다면 vue의 배포 url만 적어주면 거기서만 요청할 수 있을까? cors라 아닐 수도 있을까?.. 잘 모르겠다 나중에 해봐야 알듯.

17. `Debug=False`를 해주면 그 `api_view`가 해주는 화면이 안 보일 줄 알았는데, 그래도 보이네여 안보이게끔 세팅할 수 있을텐데, 그냥 여기까지..ㅎㅎ

18. 최종 url: https://bingbingba-todo-drf.herokuapp.com/api/v1/todo/  장고 저거 트레일링 슬래쉬 진짜 볼때마다 맘에 안듬

    

#### 2. 프론트엔드

1. 아직 미완성 된 기능이 많지만 crud는 되니까 일단 배포부터 하기로. base url을 바꿔주자.

2. github에다가 업로드.
3. netlify에서 해당 리포로 배포하기 선택.
4. 나는 yarn 을 썼으므로 build command는 `yarn build` publish directory는 `dist`이다.
5. 디플로이!
6. 프론트 배포 너무 쉽다 진짜..
7. 최종 url: https://reverent-bohr-43f0b0.netlify.app/



