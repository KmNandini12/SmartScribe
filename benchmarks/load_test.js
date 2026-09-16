import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 }, // Ramp-up to 10 users
    { duration: '1m', target: 50 },  // Sustained load: 50 concurrent uploads
    { duration: '30s', target: 0 },  // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<150'], // 95% of API requests return under 150ms
    http_req_failed: ['rate<0.01'],   // Under 1% error rate
  },
};

export default function () {
  const payload = JSON.stringify({
    title: "Engineering Retrospective",
    content: "Raw transcript text with 500 sentences and 7,500 words...",
    format: "vtt"
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const res = http.post('http://localhost:8000/api/v1/jobs/summarize', payload, params);
  
  check(res, {
    'status is 202': (r) => r.status === 202,
    'job_id present': (r) => JSON.parse(r.body).job_id !== undefined,
  });
  
  sleep(1);
}
