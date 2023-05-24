```shell
docker-compose run benchmark-redis-py-3
```

```
[+] Running 1/0
 ✔ Container redis_benchmarks-redis-1  Running                                                                                                                                                     0.0s
INFO:Benchmark:Redis server: 7.0.11, Redis client: 3.5.3, Hiredis: 2.2.3, video resolution: 1920x1080, frames count: 200
INFO:Benchmark:Pushing 200 1920x1080 frames took 0.7639216250008758 seconds (FPS 261.8069621995198)
INFO:Benchmark:Pulling 200 1920x1080 frames took 1.2506041260003258 seconds (FPS 159.9227092266509)
```

```shell
docker-compose run benchmark-redis-py-4
```

```
[+] Running 1/0
 ✔ Container redis_benchmarks-redis-1  Running                                                                                                                                                     0.0s
INFO:Benchmark:Redis server: 7.0.11, Redis client: 4.5.5, Hiredis: 2.2.3, video resolution: 1920x1080, frames count: 200
INFO:Benchmark:Pushing 200 1920x1080 frames took 2.309547250999458 seconds (FPS 86.59705919134146)
INFO:Benchmark:Pulling 200 1920x1080 frames took 2.8736540009995224 seconds (FPS 69.5978012420547)
```
