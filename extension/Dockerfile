# extension/Dockerfile
FROM node:20-alpine

LABEL maintainer="ai-guard"
LABEL description="Chrome Extension build & verification container"

WORKDIR /app

# מעתיקים את קוד התוסף
COPY . .

# בדיקות מבנה בסיסיות
RUN test -f manifest.json \
 && test -d shared

# בדיקות syntax לכל קבצי ה-JS
RUN for file in shared/*.js; do \
      echo "Checking $file"; \
      node --check "$file"; \
    done

# אם הגענו עד כאן – התוסף תקין
CMD ["sh", "-c", "echo 'Chrome extension verified successfully'"]
