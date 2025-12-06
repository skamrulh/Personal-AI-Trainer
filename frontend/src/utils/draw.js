export const drawKeypoints = (keypoints, ctx) => {
  keypoints.forEach(pt => {
    if (pt.score > 0.3) {
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 4, 0, 2 * Math.PI);
      ctx.fillStyle = 'red';
      ctx.fill();
    }
  });
};

export const drawSkeleton = (keypoints, ctx) => {
  const adjacentPairs = [
    [5, 7], [7, 9],
    [6, 8], [8, 10],
    [5, 6],
    [11, 12],
    [11, 13], [13, 15],
    [12, 14], [14, 16]
  ];

  ctx.strokeStyle = 'green';
  ctx.lineWidth = 2;

  adjacentPairs.forEach(([a,b]) => {
    if (keypoints[a].score > 0.3 && keypoints[b].score > 0.3) {
      ctx.beginPath();
      ctx.moveTo(keypoints[a].x, keypoints[a].y);
      ctx.lineTo(keypoints[b].x, keypoints[b].y);
      ctx.stroke();
    }
  });
};
