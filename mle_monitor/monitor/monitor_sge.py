from datetime import datetime
import subprocess as sp
from mle_toolbox import mle_config


def get_sge_data():
    """Helper to get all utilisation data for sge resource."""
    user_data = get_user_sge_data()
    host_data = get_host_sge_data()
    util_data = get_util_sge_data()
    return user_data, host_data, util_data


def get_user_sge_data():
    """Get jobs scheduled by Slurm cluster users.
    Return dictionary with `users`, `total`, `run`, `wait`, `login`.
    """
    user_data = {"user": [], "total": [], "run": [], "wait": [], "login": []}
    all_users = sp.check_output(["qconf", "-suserl"]).split(b"\n")[:-1]
    all_users = [u.decode() for u in all_users]
    user_cmd = [["-u", u] for u in all_users]
    user_cmd = [item for sublist in user_cmd for item in sublist]
    for user in all_users:
        try:
            queue_all = len(
                sp.check_output(
                    ["qstat", "-u", user, "-q", mle_config.sge.info.queue]
                ).split(b"\n")[:-1]
            )
            queue_all -= 2 * (queue_all != 0)

            queue_spare = len(
                sp.check_output(
                    ["qstat", "-u", user, "-q", mle_config.sge.info.spare]
                ).split(b"\n")[:-1]
            )
            queue_spare -= 2 * (queue_spare != 0)
            total_jobs = queue_all + queue_spare

            if total_jobs != 0:
                qlogins, running, waiting = 0, 0, 0
                # Get logins.
                if queue_spare != 0:
                    ps = sp.Popen(
                        ("qstat", "-u", user, "-q", mle_config.sge.info.spare),
                        stdout=sp.PIPE,
                    )
                    try:
                        qlogins = sp.check_output(("grep", "QLOGIN"), stdin=ps.stdout)
                        ps.wait()
                        qlogins = len(qlogins.split(b"\n")[:-1])
                    except Exception:
                        pass

                # Get waiting jobs.
                if queue_all != 0:
                    waiting = len(
                        sp.check_output(
                            [
                                "qstat",
                                "-s",
                                "p",  # pending
                                "-u",
                                user,
                                "-q",
                                mle_config.sge.info.queue,
                            ]
                        ).split(b"\n")[:-1]
                    )
                    waiting -= 2 * (waiting != 0)

                # Get running jobs.
                if queue_all != 0:
                    running = len(
                        sp.check_output(
                            [
                                "qstat",
                                "-s",
                                "r",
                                "-u",
                                user,
                                "-q",
                                mle_config.sge.info.queue,
                            ]
                        ).split(b"\n")[:-1]
                    )
                    running -= 2 * (running != 0)

                # Add a row for each user that has running jobs
                if qlogins + running != 0:
                    user_data["user"].append(user)
                    user_data["total"].append(total_jobs)
                    user_data["run"].append(running)
                    user_data["wait"].append(waiting)
                    user_data["login"].append(qlogins)
        except Exception:
            pass
    return user_data


def get_host_sge_data():
    """Get jobs running on different SGE cluster hosts.
    Return dictionary with `host_id`, `total`, `run`, `login`.
    """
    host_data = {"host_id": [], "total": [], "run": [], "login": []}
    try:
        all_users = sp.check_output(["qconf", "-suserl"]).split(b"\n")[:-1]
        all_users = [u.decode() for u in all_users]
        user_cmd = [["-u", u] for u in all_users]
        user_cmd = [item for sublist in user_cmd for item in sublist]
        for host_id in mle_config.sge.info.node_ids:
            queue_all, queue_spare = 0, 0
            qlogins, running = 0, 0
            cmd = ["qstat", "-q", mle_config.sge.info.queue] + user_cmd
            ps = sp.Popen(cmd, stdout=sp.PIPE)
            try:
                queue_all = sp.check_output(
                    ("grep", mle_config.sge.info.node_reg_exp[0] + host_id),
                    stdin=ps.stdout,
                )
                ps.wait()
                queue_all = len(queue_all.split(b"\n")[:-1])
            except Exception:
                pass
            cmd = ["qstat", "-q", mle_config.sge.info.spare] + user_cmd
            ps = sp.Popen(cmd, stdout=sp.PIPE)
            try:
                queue_spare = sp.check_output(
                    ("grep", mle_config.sge.info.node_reg_exp[0] + host_id),
                    stdin=ps.stdout,
                )
                ps.wait()
                # print(queue_spare)
                queue_spare = len(queue_spare.split(b"\n")[:-1])
            except Exception:
                pass

            if queue_all != 0:
                cmd = ["qstat", "-s", "r", "-q", mle_config.sge.info.queue] + user_cmd
                ps = sp.Popen(cmd, stdout=sp.PIPE)
                try:
                    running = sp.check_output(
                        ("grep", mle_config.sge.info.node_reg_exp[0] + host_id),
                        stdin=ps.stdout,
                    )
                    ps.wait()
                    running = len(running.split(b"\n")[:-1])
                except Exception:
                    pass

            # if queue_spare != 0:
            #     cmd = ["qstat", "-s", "r", "-q", mle_config.sge.info.spare] + user_cmd
            #     ps = sp.Popen(cmd, stdout=sp.PIPE)
            #     try:
            #         qlogins = sp.check_output(
            #             ("grep", mle_config.sge.info.node_reg_exp[0] + host_id),
            #             stdin=ps.stdout,
            #         )
            #         ps.wait()
            #         qlogins = len(qlogins.split(b"\n")[:-1])
            #     except Exception:
            #         pass

            # TODO: Figure out double grep and why only my jobs are found
            total_jobs = running + qlogins
            # Add a row for each host in the SGE cluster
            host_data["host_id"].append(host_id)
            host_data["total"].append(total_jobs)
            host_data["run"].append(running)
            host_data["login"].append(qlogins)
    except Exception:
        pass
    return host_data


def get_util_sge_data():
    """Get memory and CPU utilisation for specific SGE queue."""
    all_hosts = sp.check_output(["qconf", "-ss"]).split(b"\n")
    all_hosts = [u.decode() for u in all_hosts]
    # Filter list of hosts by node 'stem'
    all_hosts = list(
        filter(lambda k: mle_config.sge.info.node_reg_exp[0] in k, all_hosts)
    )

    all_cores, all_cores_util, all_mem, all_mem_util = [], [], [], []
    # Loop over all hosts and collect the utilisation data from the
    # cmd line qhost output
    for host in all_hosts:
        out = sp.check_output(["qhost", "-h", host]).split(b"\n")
        out = [u.decode() for u in out][3].split()
        cores, core_util, mem, mem_util = out[2], out[6], out[7], out[8]
        all_cores.append(float(cores))
        try:
            all_cores_util.append(float(core_util) * float(cores))
        except Exception:
            all_cores_util.append(0)
        all_mem.append(float(mem[:-1]))
        all_mem_util.append(float(mem_util[:-1]))
    return {
        "cores": sum(all_cores),
        "cores_util": sum(all_cores_util),
        "mem": sum(all_mem),
        "mem_util": sum(all_mem_util),
        "time_date": datetime.now().strftime("%m/%d/%y"),
        "time_hour": datetime.now().strftime("%H:%M:%S"),
    }
