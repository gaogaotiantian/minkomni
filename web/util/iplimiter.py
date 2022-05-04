from fastapi import Request
import functools
import time


class IpLimiter:
    CLEAN_PERIOD = 360
    def __init__(self):
        self.ip_list = {}
        self.last_clean = time.time()

    def __call__(self, period):
        def inner(func):
            functools.wraps(func)
            async def awrapper(request: Request):
                self.clean()
                ip = request.client.host
                if ip not in self.ip_list:
                    self.ip_list[ip] = {}
                else:
                    if time.time() - self.ip_list[ip]["last_visit"] < period:
                        return {"success": False, "msg": "Max access frequency exceed"}

                self.ip_list[ip]["last_visit"] = time.time()
                return await func(request)
            return awrapper
        return inner

    def clean(self):
        if time.time() - self.last_clean > self.CLEAN_PERIOD:
            clean_ip_list = []
            for ip, data in self.ip_list.items():
                if data["last_visit"] < self.last_clean:
                    clean_ip_list.apend(ip)
            for ip in clean_ip_list:
                self.ip_list.pop(ip)
            self.last_clean = time.time()


iplimiter = IpLimiter()
